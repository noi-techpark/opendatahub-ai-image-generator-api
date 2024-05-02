# -*- coding: utf-8 -*-

import requests
import pandas as pd
import os
from googletrans import Translator
translator = Translator()

def api_get(url):
    headers = {}
    response = requests.get(url, headers=headers)
    return response.json()


def fetch_all_pages(api_url):
    all_items = []
    page_number = 1

    while True:
        current_url = f"{api_url}&pagenumber={page_number}"
        page_data = api_get(current_url)

        if 'Items' in page_data and page_data['Items']:
            all_items.extend(page_data['Items'])
            page_number += 1
            print(current_url)
        else:
            break

    return all_items

#all_items = fetch_all_pages(api_url)

def process_data(api_url):
    all_items= api_get(api_url)
    def my_filtering_function(pair):
        wanted_keys = 'Items'
        key, value = pair
        if key in wanted_keys:
            return True  # keep pair in the filtered dictionary
        else:
            return False  # filter pair out of the dictionary

    if 'tourism' in api_url:
      filtered_Items = dict(filter(my_filtering_function, all_items.items()))
      df_items = pd.DataFrame.from_dict(filtered_Items['Items'])  # Creating DataFrame with 'Items' column
        # Creating DataFrame with 'Items' column
    elif 'mobility' in api_url:
      df_items = pd.DataFrame.from_records(all_items)

    

    def extract_specific_columns_and_details(df):

        if 'EventShort' in api_url:
          columns_to_keep = ['Id', 'EventTitle', 'EventDescriptionEN']

        elif 'Article' in api_url:
          columns_to_keep = ['Id', 'Type', 'Detail']

        elif 'Event' in api_url:
          columns_to_keep = ['Id', 'Type', 'Detail']

        elif 'Weather' in api_url:
          columns_to_keep = ['Id', 'evolution', 'Conditions', 'Mountain']

        elif 'Accommodation' in api_url:
          columns_to_keep = ['Id', 'AccoDetail', 'AccoType', 'AccoCategoryId']

        elif 'Venue' in api_url:
          columns_to_keep = ['Id', 'Detail']

        elif 'ActivityPoi' in api_url:
          columns_to_keep =['Id', 'Detail', 'PoiType', 'SubType']

        elif 'WebcamInfo' in api_url:
          columns_to_keep = ['Id', 'Detail', 'Shortname']

        elif 'Region' in api_url:
          columns_to_keep = ['Id', 'Detail']

        elif 'Municipality' in api_url:
          columns_to_keep = ['Id', 'Detail']

        elif 'District' in api_url:
          columns_to_keep = ['Id', 'Detail']

        elif 'SkiRegion' in api_url:
          columns_to_keep = ['Id', 'Detail']

        elif 'TourismAssociation' in api_url:
          columns_to_keep = ['Id', 'Detail']

        elif 'SkiArea' in api_url:
          columns_to_keep = ['Id', 'Detail']

        elif 'WineAward' in api_url:
          columns_to_keep = ['Id', 'Detail']

        elif 'mobility' in api_url:
          columns_to_keep = ['id']

        columns_to_drop = [col for col in df.columns if col not in columns_to_keep]
        df = df.drop(columns=columns_to_drop)
        return df
    def extract_translate(item):
        if 'AccoDetail' in item:
            accodetail_info = item['AccoDetail']
            if 'en' in accodetail_info:
                return accodetail_info['en']  # Return the 'en' section from 'AccoDetail'
        elif 'Detail' in item:
            detail_info = item['Detail']
            if 'en' in detail_info:
                return detail_info['en']  # Return the 'en' section from 'Detail'

        return None
    def acco_manager(df):
        df = extract_specific_columns_and_details(df)
        df['AccoDetail'] = df.apply(extract_translate, axis=1)

        return df

    def article_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)

        return df

    def event_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)
        return df

    def venue_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)
        return df

    def activity_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)
        return df

    def eventShort_manager(df):
        df = extract_specific_columns_and_details(df)

        return df

    def webcamInfo_manager(df):
        df = extract_specific_columns_and_details(df)
        return df

    def region_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)
        return df

    def municipality_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)
        return df

    def district_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)
        return df

    def skiRegion_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)
        return df

    def tourismAssociation_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)
        return df

    def skiArea_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)
        return df

    def wineAward_manager(df):
        df = extract_specific_columns_and_details(df)
        df['Detail'] = df.apply(extract_translate, axis=1)
        return df

    def weather_manager(df):
        df = extract_specific_columns_and_details(df)
        return df

    def mobility_manager(df):
        df = extract_specific_columns_and_details(df)
        return df

    if 'Article' in api_url:
          df = article_manager(df_items)
    elif 'EventShort' in api_url:
          df = eventShort_manager(df_items)
    elif 'Event' in api_url:
          df= event_manager(df_items)
    elif 'Weather' in api_url:
          df= weather_manager(df_items)
    elif 'Accommodation' in api_url:
          df = acco_manager(df_items)
    elif 'Venue' in api_url:
          df = venue_manager(df_items)
    elif 'ActivityPoi' in api_url:
          df = activity_manager(df_items)
    elif 'WebcamInfo' in api_url:
          df = webcamInfo_manager(df_items)
    elif 'Region' in api_url:
          df = region_manager(df_items)
    elif 'Municipality' in api_url:
          df = municipality_manager(df_items)
    elif 'District' in api_url:
          df = district_manager(df_items)
    elif 'SkiRegion' in api_url:
          df = skiRegion_manager(df_items)
    elif 'TourismAssociation' in api_url:
          df = tourismAssociation_manager(df_items)
    elif 'SkiArea' in api_url:
          df = skiArea_manager(df_items)
    elif 'WineAward' in api_url:
          df = wineAward_manager(df_items)
    elif 'mobility' in api_url:
          df = mobility_manager(df_items)
    return df
