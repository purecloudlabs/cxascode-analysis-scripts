import pandas as pd
import matplotlib.pyplot as plt

def generate_plt_by_resource_type(df,resource_type):
    """
    Generates a bar plot showing the distribution of resources by type.
    
    Args:
        df (pandas.DataFrame): Input dataframe containing resource data
        resource_type (str): Type of resource to filter and plot
        
    Returns:
        matplotlib.pyplot: Bar plot showing resource type distribution
        
    The function:
    1. Filters dataframe for specified resource type
    2. Counts occurrences of each resource
    3. Creates bar plot with resource counts
    4. Adds count labels on top of each bar
    """
    df_refresh_start = df[df['type'] == resource_type]
    counts = df_refresh_start['resource_type'].value_counts()
    print(f'The total number of resource type: {resource_type} are:{len(counts)}')

    # create a bar graph
    plt.figure(figsize=(20, 6))
    ax = counts.plot(kind='bar')
    plt.title(f'Distribution of {resource_type} by Resource')
    plt.xlabel('Resource Types')
    plt.ylabel('Count')
    plt.xticks(rotation=90)  # rotate x-axis labels for better readability

    for i, patch in enumerate(ax.patches):
        height = patch.get_height()
        plt.text(i, height + 0.4, f"{height}", ha='center', va='bottom')

    return plt    

def generate_plt_by_method_url(df,method_url):
    """
    Generates a bar plot showing the distribution of method URLs.
    
    Args:
        df (pandas.DataFrame): Input dataframe containing method URL data
        method_url (str): Method URL to filter and plot
        
    Returns:
        matplotlib.pyplot: Bar plot showing method URL distribution
        
    The function:
    1. Gets value counts of method URLs from dataframe
    2. Creates bar plot with method URL counts
    3. Adds count labels on top of each bar
    4. Formats plot with labels, title and rotated x-axis ticks
    """
    method_url_counts = df['method_url'].value_counts()
    plt.figure(figsize=(10,6))
    for i, (method_url, count) in enumerate(method_url_counts.items()):
        plt.bar(i, count)
        plt.text(i, count + 0.5, str(count), ha='center', va='bottom')
        
    plt.bar(method_url_counts.index, method_url_counts.values)
    plt.xlabel('Method URL')
    plt.ylabel('Count')
    plt.title('Total Count of Each Method URL')
    plt.xticks(rotation=90)
    plt.tight_layout()
    return plt

