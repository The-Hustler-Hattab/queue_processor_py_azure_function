import azure.functions as func
import logging

from model.db.sherif_sale_properties_alchemy import PropertySherifSale, session
from model.json.sheriff_sale_detail_model import SheriffSaleDetailModel
from service.sherief_sale_ai_service import AzureCustomModel

app = func.FunctionApp()

@app.queue_trigger(arg_name="azqueue", queue_name="sherifsalequeue",
                               connection="receiptsllc_STORAGE") 
def sheriff_queue_trigger(azqueue: func.QueueMessage):
    logging.info(f"[+] deque count: {azqueue.dequeue_count} ")
    logging.info(f"[+] message id: {azqueue.id}")
    logging.info(f"[+] message expiration time: {azqueue.expiration_time}")
    logging.info(f"[+] message insertion time: {azqueue.insertion_time}")
    logging.info(f"[+] message pop receipt: {azqueue.pop_receipt}")
    
    try:
        AzureCustomModel.process_sheriff_sale_document(azqueue.get_body().decode('utf-8'))
    except Exception as e:
        logging.error(f"An error occurred: {e}")

        
