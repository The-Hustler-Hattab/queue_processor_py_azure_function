# Azure Function Queue Processor

This project is an Azure Function written in Python that processes messages from an Azure Queue using a custom Azure Form Recognizer model and saves the results to a MySQL database.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup and Configuration](#setup-and-configuration)
- [Function Description](#function-description)
- [Deployment](#deployment)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Azure CLI
- Python 3.10+
- MySQL DB
- Azure Storage Account
- Azure Form Recognizer resource

## Setup and Configuration

1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/azure-function-queue-processor.git
    cd azure-function-queue-processor
    ```

2. **Create a Virtual Environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**

    Create a `local.settings.json` file in the root of your project and add:

    ```json
    {
    "IsEncrypted": false,
    "Values": {
        "AzureWebJobsStorage": "",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "receiptsllc_STORAGE": "<Queue URI>",
        "AzureWebJobs.sheriff_queue_trigger.Disabled": "false",
        "AZURE_FORM_RECOGNIZER_ENDPOINT": "<AI URI>",
        "AZURE_FORM_RECOGNIZER_KEY": "<AI Key>",
        "AZURE_FORM_RECOGNIZER_MODEL_ID": "<AI Model>",
        "DB_ENGINE":"<Mysql Connection String>"
    }
    }
    ```
4. **Starts Function**
    ```bash
    func start
    ```

## Function Description

This function listens to an Azure Queue, processes each message using Azure Form Recognizer, and stores the results in a MySQL database.

## Deployment

1. **Log in to Azure**
    ```bash
    az login
    ```

2. **Deploy to Azure**
    ```bash
    func azure functionapp publish <Your_FunctionApp_Name>
    ```



## Usage

1. Add messages to the Azure Queue.
2. The function processes messages and saves the results to the MySQL database.
3. Monitor the function via Azure Portal for logs and outputs.

## Troubleshooting

- Ensure all environment variables are correctly set.
- Verify Azure credentials and permissions.
- Check MySQL server connectivity and credentials.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
