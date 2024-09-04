import os
import json
import pandas as pd
from datetime import datetime
from itertools import chain
from pprint import pprint
from fuzzywuzzy import process, fuzz
from decimal import *

# from shroomdk import ShroomDK

from flipside import Flipside


SHROOM_SDK_API = os.environ["SHROOM_SDK"]

flipside = Flipside(SHROOM_SDK_API)


def querying_pagination(query_string, API_KEY=SHROOM_SDK_API):
    """
    This function queries the Flipside database using the Shroom SDK and returns a pandas dataframe

    :param query_string: SQL query string
    :param API_KEY: API key for Shroom SDK
    :return: pandas dataframe

    """

    print("query_string", query_string)
    sdk = ShroomDK(API_KEY)

    # Query results page by page and saves the results in a list
    # If nothing is returned then just stop the loop and start adding the data to the dataframe
    result_list = []
    for i in range(1, 11):  # max is a million rows @ 100k per page
        data = sdk.query(query_string, page_size=100000, page_number=i)
        if data.run_stats.record_count == 0:
            break
        else:
            result_list.append(data.records)

    # Loops through the returned results and adds into a pandas dataframe
    result_df = pd.DataFrame()
    for idx, each_list in enumerate(result_list):
        if idx == 0:
            result_df = pd.json_normalize(each_list)
        else:
            result_df = pd.concat([result_df, pd.json_normalize(each_list)])

    return result_df


# SELECT WIDGET_NAME, COUNT(*) as COUNT
# FROM near.social.fact_widget_deployments
# GROUP BY WIDGET_NAME;


def get_widget_names():

    sql_statement = """
    SELECT
    WIDGET_NAME,
    COUNT(*) as COUNT,
    MAX(BLOCK_TIMESTAMP) as LATEST_TIMESTAMP
    FROM near.social.fact_widget_deployments
    WHERE BLOCK_TIMESTAMP >= CURRENT_DATE()-60
    GROUP BY WIDGET_NAME
    ORDER BY LATEST_TIMESTAMP DESC;
    """
    snowflake_data = flipside.query(sql_statement)
    return snowflake_data.records


def get_dev_info(dev_name):

    sql_statement = f"""

    select * from
    near.social.fact_profile_changes
    where signer_id = '{dev_name}'
    and profile_section = 'linktree'
    order by BLOCK_TIMESTAMP asc
    limit 1
    """

    snowflake_data = flipside.query(sql_statement)
    return snowflake_data.records


def get_list_of_all_devs():

    sql_statement = f"""
    SELECT signer_id, COUNT(*) as COUNT
    FROM near.social.fact_widget_deployments
    GROUP BY signer_id;

    """

    snowflake_data = flipside.query(sql_statement)
    snowflake_data = snowflake_data.records
    signer_ids = [row["signer_id"] for row in snowflake_data]

    data = set(signer_ids)
    return data


def get_widget_updates(widget_name, timestamp=None):

    widget_name = widget_name.replace("'", "\\'")

    if timestamp:
        sql_statement = f"""
        SELECT *
        FROM near.social.fact_widget_deployments
        WHERE WIDGET_NAME = '{widget_name}'
        AND BLOCK_TIMESTAMP > '{timestamp}';
        """
    else:

        sql_statement = f"""
        select * from
        near.social.fact_widget_deployments
        where WIDGET_NAME = '{widget_name}'
        """

    snowflake_data = flipside.query(sql_statement)
    return snowflake_data.records

    """
    This function queries transactions received by address and returns the top n addresses

    :param top_n: number of top addresses to return
    :param time_period: time period to query
    :return: pandas dataframe

    """

    # sql_statement =f"""
    # SELECT
    #     tx_signer,
    #     COUNT(*)
    # FROM
    #     near.CORE.fact_transactions
    # WHERE
    #     block_timestamp > (CURRENT_DATE() - INTERVAL '{time_period}')
    #     AND tx_status = 'Success'
    # GROUP BY
    #     tx_signer
    # ORDER BY
    #     COUNT(*) DESC
    # LIMIT {top_n}
    # """
