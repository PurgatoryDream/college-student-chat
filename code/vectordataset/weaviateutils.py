import weaviate
client = weaviate.Client("http://weaviate:8080")

# Create a new schema for the vector dataset:
def create_schema(vector_class_name, vectorizer):
    vector_dataset_obj = {
        "class": vector_class_name,
        "vectorizer": vectorizer,
    }
    client.schema.create_class(vector_dataset_obj)

# Send a new batch of vectors to Weaviate:
def send_vectors(data, vector_class_name, vector_values):
    with client.batch as batch:
        batch.batch_size = 50
        batch.dynamic = True
        for i, data_obj in enumerate(data):
            batch.add_data_object(
                data_obj,
                vector_class_name,
                vector=vector_values[i]
            )

# Delete vectors with a given filename:
def delete_vector(vector_class_name, filename):
    with client.batch as batch:
        batch.delete_objects(
            vector_class_name,
            where={
                "path": ['filename'],
                "operator": "Equal",
                "valueText": filename
            }
        )

# Retrieve the vector values from Weaviate:
def get_vector_values(vector_class_name, vector_query):
    results = client.query.get(
        vector_class_name, ["filename", "text", "author", "date", "source"]
    ).with_near_vector(
        {"vector": vector_query}
    ).with_additional(
        ["distance", "id"]
    ).with_limit(5).do()
    return results['data']['Get'][vector_class_name]

if __name__ == "__main__":
    create_schema("LearningMaterial", "none")