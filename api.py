from flask import Flask, jsonify, render_template, request, redirect, url_for
import os
import shutil
import requests
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

import ai_img_single
import dataframe_generation
import ai_img_generate_single

app = Flask(__name__, static_folder='static', template_folder='templates')

# AWS S3 configuration
s3_image_urls = []

AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'
S3_BUCKET_NAME = 'opendatahub.ai-generated-images'
AWS_REGION = 'eu-west-1'

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

app.config['BASE_URL'] = f"https://s3.{AWS_REGION}.amazonaws.com/{S3_BUCKET_NAME}"


def move_image_to_saved(image_filename):
    source_path = f"images/{image_filename}"
    dest_path = f"saved/{image_filename}"

    try:
        s3_client.copy_object(Bucket=S3_BUCKET_NAME, CopySource=f"{S3_BUCKET_NAME}/{source_path}", Key=dest_path)

        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=source_path)

        print(f"Image {image_filename} moved to 'saved' folder in S3 bucket.")
    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"Error moving image: {e}")

def delete_image(image_filename):
    source_path = f"images/{image_filename}"

    try:

        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=source_path)

        print(f"Image {image_filename} was deleted.")
    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"Error deleting image: {e}")

def show_image_info(df, image_name):
    try:
        matching_row = df[df['Id'] == image_name]

        if not matching_row.empty:
            print(matching_row.to_dict('records')[0])  # Print the row as a dictionary
            return {'item': matching_row.to_dict('records')[0]}

        return f"Image with name {image_name} not found in the DataFrame."

    except ValueError as ve:
        return f"Error parsing DataFrame: {ve}"

@app.route('/')
def display_image():
    section = request.args.get('section', 'Accommodation')  # Default to Accommodation if not provided
    selected_filter = request.args.get('filter', 'all')  # Default to 'all' if not provided
    s3_objects = s3_client.list_objects(Bucket=S3_BUCKET_NAME)
    s3_image_urls = [f"https://s3.{AWS_REGION}.amazonaws.com/{S3_BUCKET_NAME}/{obj['Key']}" for obj in s3_objects.get('Contents', [])]

    if not s3_image_urls:
        return "No more images available."

    # Fetch DataFrame
    json_url = f"https://tourism.opendatahub.com/v1/{section}?pagenumber=1"
    df = dataframe_generation.process_data(json_url)

    # Filter S3 images based on DataFrame IDs
    filtered_s3_images = [url for url in s3_image_urls if os.path.basename(url).split('.')[0] in df['Id'].tolist()]
    single_image_url = filtered_s3_images[0] if filtered_s3_images else None

    if single_image_url:
        single_image_info = show_image_info(df, os.path.basename(single_image_url).split('.')[0])

    else:
        single_image_info = None
    # Provide the first image for single image view
    return render_template("img_table.html", s3_image_urls=filtered_s3_images, df=df, section=section,
                           single_image_url=single_image_url, single_image_info=single_image_info, os = os,
                           show_image_info = show_image_info, selected_filter=selected_filter,  base_url=app.config['BASE_URL'])


@app.route('/process_choice', methods=['POST'])
def process_choice():
    choice = request.form['choice']
    section = request.form['section']
    image_url = request.form['imageUrl']

    if choice == 'save':
        if image_url:
            image_filename = os.path.basename(image_url)
            move_image_to_saved(image_filename)

            return jsonify({'status': 'success', 'message': 'Image saved correctly'})
    elif choice == 'delete':
        if image_url:
            image_filename = os.path.basename(image_url)
            delete_image(image_filename)
            return jsonify({'status':'success','message': 'Image deleted correctly'})
    elif choice == 'regenerate':
        if image_url:
            image_filename = os.path.basename(image_url)
            delete_image(image_filename)

        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Failed to save image'})

@app.route('/generate', methods=['GET'])
def display_single_image():
    section = request.args.get('section')
    imageId = request.args.get('imageId')

    if not imageId:
        return render_template("single_image.html", error_message="Image ID is required.", imageId=None, image_info={})

    bucket = S3_BUCKET_NAME
    key = f'images/{imageId}.png'

    try:
        # Check if the image exists in the S3 bucket
        s3_client.head_object(Bucket=bucket, Key=key)
        # Image exists in S3, display it
        image_url = f"{app.config['BASE_URL']}/{key}"
        json_url = f"https://tourism.opendatahub.com/v1/{section}/{imageId}"
        df = ai_img_generate_single.process_dataframe(json_url)

        if not df.empty:
            image_info = df.to_dict(orient='records')[0]
            return render_template("single_image.html", imageId=imageId, image_url=image_url, image_info=image_info, section=section)
    except NoCredentialsError:
        # Handle the case when AWS credentials are missing
        return render_template(
            "single_image.html", error_message="AWS credentials are missing.", imageId=imageId, image_info={}
        )
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            # Image not found in S3, generate it
            return render_template(
                "single_image.html", error_message="Image not found.", imageId=imageId, image_info={}, generate_image_url=url_for('generate_image', imageId=imageId, section=section)
            )
    except Exception:
        return render_template(
            "single_image.html", error_message="Error retrieving image.", imageId=imageId, image_info={}
        )
@app.route('/generate_image/<section>/<imageId>', methods=['GET'])
def generate_image(section, imageId):
    json_url = f"https://tourism.opendatahub.com/v1/{section}/{imageId}"
    df = ai_img_generate_single.process_dataframe(json_url)
    image_info = df.to_dict(orient='records')[0]

    print("Generated Image Info:", image_info)

    return render_template("single_image.html", imageId=imageId, image_info=image_info, section=section)




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)