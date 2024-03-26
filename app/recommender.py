import sqlite3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


def get_important_features(data):
    important_features = []
    for i in range(0, data.shape[0]):
        important_features.append(
            data['category_name'][i] + " " +
            str(data['parent_category_name'][i]) + " " +
            data['shop_name'][i]
        )

    return important_features

def sum_up(ids, cs):
    lists = []
    results = []
    for id in ids:
        lists.append(list(cs[id]))

    for i in range(len(lists[0])):
        results.append(0)

    for j in range(len(lists)):

        for i in range(len(lists[j])):
            results[i] += lists[j][i]
    return results


def get_similar(category_names):
    cnx = sqlite3.connect('db.sqlite3')
    sql = "SELECT " \
          "app_category.id AS category_id," \
          "app_category.name AS category_name," \
          "parent_category.name AS parent_category_name," \
          "app_shop.name AS shop_name FROM " \
          "app_category " \
          "INNER JOIN app_shop ON app_category.shop_id = app_shop.id " \
          "LEFT JOIN app_category AS parent_category ON app_category.category_id = parent_category.id"
    df = pd.read_sql(sql, cnx)
    df.head()
    #print(df.head())
    df['important_features'] = get_important_features(df)
    #print(df.head())
    cm = CountVectorizer().fit_transform(df['important_features'])
    cs = cosine_similarity(cm)
    #print(cs)
    index = []
    for category_name in category_names:
        #print(category_name)
        #print(df.head())
        index.append(df[df.category_name == category_name].index.values.astype(int)[0])

    scores = list(enumerate(sum_up(index, cs)))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    sorted_scores = sorted_scores[0:]

    #print(sorted_scores)
    newSet = set()
    j = 0
    similar_ids = []
    for item in sorted_scores:
        # print(item[0])
        category_name = df[df.index == item[0]]['category_name'].values[0]
        category_id = df[df.index == item[0]]['category_id'].values.astype(int)[0]
        # print(j + 1, category_name, "(", category_id, ")")
        j = j + 1
        if category_id not  in similar_ids:
            similar_ids.append(category_id)

        #newSet.add(category_id)
    #
    return similar_ids
