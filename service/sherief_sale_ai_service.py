
import logging
import time
import random

from model.constants import Constants
from model.db.sherif_sale_properties_alchemy import Property, PropertySherifSale
from model.json.sheriff_sale_detail_model import SheriffSaleDetailModel
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.polling import LROPoller
from azure.core.credentials import AzureKeyCredential

endpoint = Constants.AZURE_FORM_RECOGNIZER_ENDPOINT
key = Constants.AZURE_FORM_RECOGNIZER_KEY
model_id = Constants.AZURE_FORM_RECOGNIZER_MODEL_ID



document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)




class AzureCustomModel:
    
    @staticmethod
    def process_sheriff_sale_document(sheriff_sale_detail_model_json_str: str) :
        logging.info('[+] converting json string to object "%s"', sheriff_sale_detail_model_json_str)
        # convert the json string to object
        sheriff_sale_detail_model: SheriffSaleDetailModel = SheriffSaleDetailModel.from_json(sheriff_sale_detail_model_json_str)
        logging.info('[+] processing sheriff sale document')

        # process the object
        property_list: list[Property] = AzureCustomModel.extract_sherif_sale_details(sheriff_sale_detail_model)
        logging.info('[+] saving sheriff sale to db')
        # save the object to db
        PropertySherifSale.save_all_sherif_sales_to_db(property_list)
        logging.info('[+] process completed')
        
        
        

    @staticmethod
    def extract_sherif_sale_details(sheriff_sale_detail_model: SheriffSaleDetailModel) -> list[Property]:
        """
        Extracts sheriff sale details from a document using an Azure Custom Model with retry logic for handling rate limits.

        Args:
            sheriff_sale_detail_model (SheriffSaleDetailModel): The model containing the details of the sheriff sale document.

        Returns:
            list[Property]: A list of Property objects extracted from the document.

        Raises:
            Exception: If the document processing fails after the maximum number of retries.
        """

        retries = 5  # Maximum number of retries
        delay = 1  # Initial delay in seconds
        for attempt in range(retries):
            try:
                # Begin analyzing the document from URL
                poller: LROPoller[AnalyzeResult] = document_analysis_client.begin_analyze_document_from_url( # type: ignore
                    model_id,
                    f"https://receiptsllc.blob.core.windows.net/sherifsale/{sheriff_sale_detail_model.file_path}"
                )
                
                poller_result = poller.result()
                    
                property_list: list[Property] = []
                # Extract property details from the analyzed document

                result = poller_result.documents[0].fields.get("property").value
                for item in result:
                    property = Property()
                    property.sale = item.value.get("Sale").value[:254] if item.value.get("Sale") and item.value.get("Sale").value else ""
                    property.case_number = item.value.get("caseNum").value[:254] if item.value.get("caseNum") and item.value.get("caseNum").value else ""
                    property.sale_type = item.value.get("SaleType").value[:254] if item.value.get("SaleType") and item.value.get("SaleType").value else ""
                    property.status = item.value.get("Status").value[:254] if item.value.get("Status") and item.value.get("Status").value else ""
                    property.tracts = item.value.get("Tracts").value[:254] if item.value.get("Tracts") and item.value.get("Tracts").value else ""
                    property.cost_tax_bid = item.value.get("CostTaxBid").value[:254] if item.value.get("CostTaxBid") and item.value.get("CostTaxBid").value else ""
                    property.plaintiff = item.value.get("Plantiff").value[:254] if item.value.get("Plantiff") and item.value.get("Plantiff").value else ""
                    property.attorney_for_plaintiff = item.value.get("AttorneyForPlantiff").value[:254] if item.value.get("AttorneyForPlantiff") and item.value.get("AttorneyForPlantiff").value else ""
                    property.defendant = item.value.get("Defendents").value[:254].replace("\n", " ") if item.value.get("Defendents") and item.value.get("Defendents").value else ""
                    property.property_address = item.value.get("PropertyAddress").value[:254].replace("\n", " ") if item.value.get("PropertyAddress") and item.value.get("PropertyAddress").value else ""
                    property.municipality = item.value.get("Municipality").value[:254] if item.value.get("Municipality") and item.value.get("Municipality").value else ""
                    property.parcel_tax_id = item.value.get("ParcelTaxId").value[:254] if item.value.get("ParcelTaxId") and item.value.get("ParcelTaxId").value else ""
                    property.comments = item.value.get("Comments").value[:254] if item.value.get("Comments") and item.value.get("Comments").value else ""
                    property.SHERIEF_SALE_CHILD_ID = sheriff_sale_detail_model.sheriff_sale_child_id
                    if property.tracts == "1":
                        address = property.property_address.replace(" ", "-")
                        zillow_link = f"https://www.zillow.com/homes/{address}_rb/"
                        property.zillow_link = zillow_link
                    else:
                        property.zillow_link = ""

                    property_list.append(property)
                return property_list

            except Exception as e:
                if '429' in str(e):  
                    wait_time = delay * (2 ** attempt) + random.uniform(0, 1)
                    logging.error(f"Rate limit hit. Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"An error occurred: {e}")
                    raise e  # Re-raise the exception if it's not a 429 error
        
        logging.info("Max retries reached. Could not process document.")
        raise Exception("Max retries reached")
