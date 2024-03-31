#!/bin/bash

if ! command -v docker &> /dev/null; then
    echo "Docker could not be found. Please install Docker and try again."
    exit 1
fi

echo "Docker is installed."

mkdir -p documents
echo "----------------------------------------------------------------------------------------------------"
echo "Please ensure you have installed the required packages by running 'pip install -r requirements.txt'."
echo "Please ensure your PDF file is placed in the NLP-vec-prep/documents directory."
echo "Please ensure you edit the config_template.json file and save it as config.json"
echo "----------------------------------------------------------------------------------------------------"

container_exists=$(docker ps -a --filter "name=ollama" --format "{{.Names}}")

if [ "$container_exists" ]; then
    echo "An existing Ollama container was found. Do you want to start it? (yes/no)"
    read -r start_existing_container
    if [[ "$start_existing_container" == "yes" ]]; then
        docker start ollama
    else
        echo "A new Ollama container will be set up."
        docker pull ollama/ollama
        docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    fi
else
    echo "Setting up a new Ollama container..."
    docker pull ollama/ollama
    docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
fi
echo "----------------------------------------------------------------------------------------------------"
echo "Do you want to use a Modelfile? (yes/no)"
echo "If so, please ensure you have placed the Modelfile in the NLP-vec-prep directory."
read -r use_modelfile

if [[ "$use_modelfile" == "yes" ]]; then
    docker exec ollama mkdir -p /files
    docker cp ./Modelfile ollama:/files/Modelfile
    echo "Enter the model name to create using the Modelfile: "
    read -r modelname
    docker exec -it ollama ollama create "$modelname" -f /files/Modelfile
    docker exec -it ollama ollama list
else
    echo "Skipping Modelfile steps."
fi
echo "----------------------------------------------------------------------------------------------------"
echo "Start"
python3 process/main.py
