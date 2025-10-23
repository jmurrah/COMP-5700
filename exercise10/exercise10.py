"""
COMP-5700 Exercise 10: Access Control
Author: Jacob Murrah
Date: 10/27/2025
"""

import pandas as pd
import yaml

# Function to read the data in the spreadsheet [10%]
def read_data(file_path):
    data = pd.read_excel(file_path)
    file_columns = data.columns[1:]
    data[file_columns] = data[file_columns].map(
        lambda x: str(int(x)) if pd.notna(x) else ""
    )
    return data


# Function to answer query #1 [10%]
def number_of_users_with_777_permission_for_all_files(data: pd.DataFrame) -> int:
    file_columns = data.columns[1:]
    mask = (data[file_columns] == "777").all(axis=1)
    return mask.sum()


# Function to answer query #2 [10%]
def number_of_users_with_777_permission_for_any_file(data: pd.DataFrame) -> int:
    file_columns = data.columns[1:]
    mask = (data[file_columns] == "777").any(axis=1)
    return mask.sum()


# Function to answer query #3 [10%]
def number_of_users_with_444_permission_for_all_files(data: pd.DataFrame) -> int:
    file_columns = data.columns[1:]
    mask = (data[file_columns] == "444").all(axis=1)
    return mask.sum()


# Function to answer query #4 [10%]
def number_of_users_with_444_permission_for_any_file(data: pd.DataFrame) -> int:
    file_columns = data.columns[1:]
    mask = (data[file_columns] == "444").any(axis=1)
    return mask.sum()


# Function to answer query #5 [10%]
def number_of_users_with_read_permission_for_any_file(data: pd.DataFrame) -> int:
    # NOTE: read permission is granted to digits >= 4.
    file_columns = data.columns[1:]
    mask = data[file_columns].map(lambda x: any(d >= "4" for d in x)).any(axis=1)
    return mask.sum()


# Function to answer query #6 [10%]
def number_of_users_with_no_permissions_for_all_files(data: pd.DataFrame) -> int:
    file_columns = data.columns[1:]
    mask = (data[file_columns] == "").all(axis=1)
    return mask.sum()


# Function to implement hashmap [20%]
def generate_hashmap_for_users_with_permissions_for_atleast_2_files(
    data: pd.DataFrame,
) -> dict:
    hashmap = {}

    file_columns = data.columns[1:]
    for _, row in data.iterrows():
        permissions, count = [], 0
        for column in file_columns:
            if row[column] != "":
                permissions.append(
                    {
                        "file": column,
                        "permission": row[column],
                    }
                )
                count += 1

        if count >= 2:
            hashmap[row["USERID"]] = permissions

    return hashmap


# Function to generate YAML file from hashmap [8%] + [2%]
def export_hashmap_to_yaml_file(hashmap: dict, output_file: str) -> None:
    with open(output_file, "w") as file:
        yaml.dump(hashmap, file)


if __name__ == "__main__":
    data = read_data("data.xlsx")

    print("All 777:", number_of_users_with_777_permission_for_all_files(data))
    print("Any 777:", number_of_users_with_777_permission_for_any_file(data))
    print("All 444:", number_of_users_with_444_permission_for_all_files(data))
    print("Any 444:", number_of_users_with_444_permission_for_any_file(data))
    print("Any read:", number_of_users_with_read_permission_for_any_file(data))
    print("All none:", number_of_users_with_no_permissions_for_all_files(data))

    hashmap = generate_hashmap_for_users_with_permissions_for_atleast_2_files(data)
    export_hashmap_to_yaml_file(hashmap, "output.yaml")
