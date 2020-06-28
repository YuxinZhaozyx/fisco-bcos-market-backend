from django.shortcuts import render
from django.http import JsonResponse

from client.contractnote import ContractNote
from client.datatype_parser import DatatypeParser
from client.bcosclient import BcosClient

# Create your views here.

def create_user(request):
    user_id = request.POST.get('user_id')
    user_password = request.POST.get('user_password')
    balance = int(request.POST.get('balance'))
    info = request.POST.get('info')

    contract_name = "Admin"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "create_user", [user_id, user_password, balance, info])
    txhash = receipt['transactionHash']
    txresponse = client.getTransactionByHash(txhash)
    inputresult = data_parser.parse_transaction_input(txresponse['input'])
    res = data_parser.parse_receipt_output(inputresult['name'], receipt['output'])
    client.finish()

    code_map = {
        0: 0,  # success 
        -1: -1,  # user already exists
        -2: -2,  # unknown error
    }
    ret_code = code_map[res[0]]

    if ret_code == 0: # success create user
        contract_name = "Admin"
        contract_address = ContractNote.get_last(contract_name)

        abi_file = f"contracts/{contract_name}.abi"
        data_parser = DatatypeParser()
        data_parser.load_abi_file(abi_file)
        contract_abi = data_parser.contract_abi

        client = BcosClient()
        receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "login", [user_id, user_password])
        client.finish()

    return JsonResponse({"code": ret_code})


def auth_user(request):
    user_id = request.POST.get('user_id')
    user_password = request.POST.get('user_password')

    contract_name = "Admin"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "valid_psd", [user_id, user_password])
    client.finish()

    code_map = {
        1: 0,  # success 
        -1: -1,  # user don't exists
        -2: -2,  # wrong password
    }
    ret_code = code_map[res[0]]

    return JsonResponse({"code": ret_code})

def get_user_info(request):
    user_id = request.POST.get('user_id')
    
    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "get_user_info", [user_id])
    client.finish()

    user_info = {
        "id": res[0],
        "info": res[1],
        "balance": res[2],
        "state": res[3],
    }

    ret_code = 0 if user_info["state"] != -999 else -1
    response = {
        "code": ret_code,
    }
    if ret_code == 0:
        response["user"] = user_info

    return JsonResponse(response)

def get_commodity_info(request):
    commodity_id = int(request.POST.get('commodity_id'))
    
    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "get_commodity_info", [commodity_id])
    client.finish()

    commodity_info = {
        "owner": res[0],
        "name": res[1],
        "image": res[2],
        "desc": res[3],
        "price": res[4],
        "state": res[5],
        "id": res[6],
        "type": res[7],
    }

    ret_code = 0 if commodity_info["state"] != -999 else -1
    response = {
        "code": ret_code,
    }
    if ret_code == 0:
        response["commodity"] = commodity_info

    return JsonResponse(response)


def get_transaction_info(request):
    transaction_id = int(request.POST.get('transaction_id'))
    
    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "get_transaction_info", [transaction_id])
    client.finish()

    transaction_info = {
        "user_id_sell": res[1],
        "user_id_buy": res[2],
        "desc": res[3],
        "commodity_id": res[4],
        "price": res[5],
        "state": res[6],
        "id": transaction_id,
    }

    ret_code = 0 if transaction_info["state"] != -999 else -1
    response = {
        "code": ret_code,
    }
    if ret_code == 0:
        response["transaction"] = transaction_info

    return JsonResponse(response)

def get_arbitration_list(request):
    max_item_count = request.POST.get("page_max_items")
    page_id = request.POST.get("page_id")
    if max_item_count is None or page_id is None:
        max_item_count = page_id = None
    else:
        max_item_count = int(max_item_count)
        page_id = int(page_id)
        if max_item_count < 1 or page_id < 0:
            max_item_count = page_id = None

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "get_arbitration_list", [])
    
    transaction_id_list, _ = res
    transaction_list = []
    transaction_count = 0
    for transaction_id in transaction_id_list:
        res = client.call(contract_address, contract_abi, "get_transaction_info", [transaction_id])
        transaction_info = {
            "user_id_sell": res[1],
            "user_id_buy": res[2],
            "desc": res[3],
            "commodity_id": res[4],
            "price": res[5],
            "state": res[6],
            "id": transaction_id,
        }
        ret_code = 0 if transaction_info["state"] != -999 else -1
        if ret_code == 0:
            transaction_list.append(transaction_info)
            transaction_count += 1

    client.finish()
    
    if max_item_count is None:
        page_num = 1 if len(transaction_list) > 0 else 0
    else:
        page_num = (len(transaction_list) + max_item_count - 1) // max_item_count
        transaction_list = transaction_list[page_id * max_item_count: (page_id + 1) * max_item_count]

    return JsonResponse({
        "transaction_list": transaction_list,
        "page_num": page_num,
    })

def get_arbitration_reason(request):
    transaction_id = int(request.POST.get('transaction_id'))
    
    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "get_arbitration_reason", [transaction_id])
    client.finish()

    arbitration_reason = res[0]

    if arbitration_reason == "NULL":
        ret_code = -1   # no such transaction
        arbitration_reason = ""
    else:
        ret_code = 0    # success

    return JsonResponse({
        "code": ret_code,
        "arbitration_reason": arbitration_reason,
    })

def search_commodity(request):
    keywords = request.POST.get("keywords")
    keywords = [keyword for keyword in keywords.split(' ') if len(keyword) > 0]
    commodity_type = request.POST.get("commodity_type")

    max_item_count = request.POST.get("page_max_items")
    page_id = request.POST.get("page_id")
    if max_item_count is None or page_id is None:
        max_item_count = page_id = None
    else:
        max_item_count = int(max_item_count)
        page_id = int(page_id)
        if max_item_count < 1 or page_id < 0:
            max_item_count = page_id = None

    if commodity_type is None:
        query_method = "get_onsale_list"
        query_args = []
    else:
        commodity_type = int(commodity_type)
        query_method = "get_onsale_type_list"
        query_args = [commodity_type]

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, query_method, query_args)

    commodity_id_list, commodity_count = res
    commodity_list = []
    for commodity_id in commodity_id_list:
        commodity_info = client.call(contract_address, contract_abi, "get_commodity_info", [commodity_id])
        commodity_info = {
            "owner": commodity_info[0],
            "name": commodity_info[1],
            "image": commodity_info[2],
            "desc": commodity_info[3],
            "price": commodity_info[4],
            "state": commodity_info[5],
            "id": commodity_info[6],
            "type": commodity_info[7],
        }
        if commodity_info["state"] != -999:
            commodity_list.append(commodity_info)
    
    client.finish()
    
    commodity_match_score_list = []
    for commodity_info in commodity_list:
        score = 0
        for keyword in keywords:
            score += int(keyword.lower() in commodity_info["name"].lower())
            score += int(keyword.lower() in commodity_info["desc"].lower())
        commodity_match_score_list.append(score)

    commodity_list = [item[0] for item in sorted(iter(i for i in zip(commodity_list, commodity_match_score_list) if i[1] > 0), key=lambda x:x[1], reverse=True)]

    if max_item_count is None:
        page_num = 1 if len(commodity_list) > 0 else 0
    else:
        page_num = (len(commodity_list) + max_item_count - 1) // max_item_count
        commodity_list = commodity_list[page_id * max_item_count: (page_id + 1) * max_item_count]

    return JsonResponse({
        "commodity_list": commodity_list,
        "page_num": page_num,
    })
            



def market_commodity_list(request):
    commodity_type = request.POST.get("commodity_type")

    max_item_count = request.POST.get("page_max_items")
    page_id = request.POST.get("page_id")
    if max_item_count is None or page_id is None:
        max_item_count = page_id = None
    else:
        max_item_count = int(max_item_count)
        page_id = int(page_id)
        if max_item_count < 1 or page_id < 0:
            max_item_count = page_id = None
    
    if commodity_type is None:
        query_method = "get_onsale_list"
        query_args = []
    else:
        commodity_type = int(commodity_type)
        query_method = "get_onsale_type_list"
        query_args = [commodity_type]

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, query_method, query_args)

    commodity_id_list, commodity_count = res
    commodity_list = []
    for commodity_id in commodity_id_list:
        commodity_info = client.call(contract_address, contract_abi, "get_commodity_info", [commodity_id])
        commodity_info = {
            "owner": commodity_info[0],
            "name": commodity_info[1],
            "image": commodity_info[2],
            "desc": commodity_info[3],
            "price": commodity_info[4],
            "state": commodity_info[5],
            "id": commodity_info[6],
            "type": commodity_info[7],
        }
        if commodity_info["state"] != -999:
            commodity_list.append(commodity_info)
    
    client.finish()
    
    if max_item_count is None:
        page_num = 1 if len(commodity_list) > 0 else 0
    else:
        page_num = (len(commodity_list) + max_item_count - 1) // max_item_count
        commodity_list = commodity_list[page_id * max_item_count: (page_id + 1) * max_item_count]

    return JsonResponse({
        "commodity_list": commodity_list,
        "page_num": page_num,
    })

def user_commodity_list(request):
    user_id = request.POST.get('user_id')

    max_item_count = request.POST.get("page_max_items")
    page_id = request.POST.get("page_id")
    if max_item_count is None or page_id is None:
        max_item_count = page_id = None
    else:
        max_item_count = int(max_item_count)
        page_id = int(page_id)
        if max_item_count < 1 or page_id < 0:
            max_item_count = page_id = None

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "get_commodity_list", [user_id])
    
    commodity_id_list, commodity_count = res
    commodity_list = []
    for commodity_id in commodity_id_list:
        commodity_info = client.call(contract_address, contract_abi, "get_commodity_info", [commodity_id])
        commodity_info = {
            "owner": commodity_info[0],
            "name": commodity_info[1],
            "image": commodity_info[2],
            "desc": commodity_info[3],
            "price": commodity_info[4],
            "state": commodity_info[5],
            "id": commodity_info[6],
            "type": commodity_info[7],
        }
        if commodity_info["state"] != -999:
            commodity_list.append(commodity_info)
    
    client.finish()

    if max_item_count is None:
        page_num = 1 if len(commodity_list) > 0 else 0
    else:
        page_num = (len(commodity_list) + max_item_count - 1) // max_item_count
        commodity_list = commodity_list[page_id * max_item_count: (page_id + 1) * max_item_count]

    return JsonResponse({
        "commodity_list": commodity_list,
        "page_num": page_num,
    })
    


def create_commodity(request):
    user_id = request.POST.get('user_id')
    commodity_name = request.POST.get('commodity_name')
    commodity_desc = request.POST.get('commodity_desc')
    commodity_image = request.POST.get('commodity_image')

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "create_commodity", [user_id, commodity_name, commodity_image, commodity_desc])
    txhash = receipt['transactionHash']
    txresponse = client.getTransactionByHash(txhash)
    inputresult = data_parser.parse_transaction_input(txresponse['input'])
    res = data_parser.parse_receipt_output(inputresult['name'], receipt['output'])
    client.finish()

    code_map = {
        1: 0,  # success 
        -1: -1,  # user state error
        -2: -2,  # unknown error
    }
    
    ret_code = code_map[res[0]]

    return JsonResponse({"code": ret_code})


def delete_commodity(request):
    user_id = request.POST.get('user_id')
    commodity_id = int(request.POST.get('commodity_id'))

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "delete_commodity", [user_id, commodity_id])
    txhash = receipt['transactionHash']
    txresponse = client.getTransactionByHash(txhash)
    inputresult = data_parser.parse_transaction_input(txresponse['input'])
    res = data_parser.parse_receipt_output(inputresult['name'], receipt['output'])
    client.finish()

    code_map = {
        1: 0,  # success 
        -1: -1,  # user state error
        -2: -2,  # unknown error
    }
    
    ret_code = code_map[res[0]]

    return JsonResponse({"code": ret_code})

def up_commodity(request):
    user_id = request.POST.get('user_id')
    commodity_id = int(request.POST.get('commodity_id'))
    commodity_price = int(request.POST.get('price'))
    commodity_type = int(request.POST.get('commodity_type'))

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "puton_commodity", [user_id, commodity_id, commodity_price, commodity_type])
    txhash = receipt['transactionHash']
    txresponse = client.getTransactionByHash(txhash)
    inputresult = data_parser.parse_transaction_input(txresponse['input'])
    res = data_parser.parse_receipt_output(inputresult['name'], receipt['output'])
    client.finish()

    code_map = {
        1: 0,  # success 
        -1: -1,  # user state error
        -2: -2,  # unknown error
    }
    ret_code = code_map[res[0]]

    return JsonResponse({"code": ret_code})

def down_commodity(request):
    user_id = request.POST.get('user_id')
    commodity_id = int(request.POST.get('commodity_id'))

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "putdown_commodity", [user_id, commodity_id])
    txhash = receipt['transactionHash']
    txresponse = client.getTransactionByHash(txhash)
    inputresult = data_parser.parse_transaction_input(txresponse['input'])
    res = data_parser.parse_receipt_output(inputresult['name'], receipt['output'])
    client.finish()

    code_map = {
        1: 0,  # success 
        -1: -1,  # user state error
        -2: -2,  # unknown error
    }
    ret_code = code_map[res[0]]

    return JsonResponse({"code": ret_code})

def user_transaction_buy_list(request):
    user_id = request.POST.get('user_id')

    max_item_count = request.POST.get("page_max_items")
    page_id = request.POST.get("page_id")
    if max_item_count is None or page_id is None:
        max_item_count = page_id = None
    else:
        max_item_count = int(max_item_count)
        page_id = int(page_id)
        if max_item_count < 1 or page_id < 0:
            max_item_count = page_id = None

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    buy_res = client.call(contract_address, contract_abi, "get_transaction_buy_list", [user_id])

    transaction_buy_list = []
    transaction_buy_count = 0
    for transaction_id in buy_res[0]:
        res = client.call(contract_address, contract_abi, "get_transaction_info", [transaction_id])
        transaction_info = {
            "user_id_sell": res[1],
            "user_id_buy": res[2],
            "desc": res[3],
            "commodity_id": res[4],
            "price": res[5],
            "state": res[6],
            "id": transaction_id,
        }
        ret_code = 0 if transaction_info["state"] != -999 else -1
        if ret_code == 0:
            transaction_buy_list.append(transaction_info)
            transaction_buy_count += 1

    client.finish()

    if max_item_count is None:
        page_num = 1 if len(transaction_buy_list) > 0 else 0
    else:
        page_num = (len(transaction_buy_list) + max_item_count - 1) // max_item_count
        transaction_buy_list = transaction_buy_list[page_id * max_item_count: (page_id + 1) * max_item_count]


    return JsonResponse({
        "transaction_list": transaction_buy_list,
        "page_num": page_num,
    })

def user_transaction_sell_list(request):
    user_id = request.POST.get('user_id')

    max_item_count = request.POST.get("page_max_items")
    page_id = request.POST.get("page_id")
    if max_item_count is None or page_id is None:
        max_item_count = page_id = None
    else:
        max_item_count = int(max_item_count)
        page_id = int(page_id)
        if max_item_count < 1 or page_id < 0:
            max_item_count = page_id = None

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    sell_res = client.call(contract_address, contract_abi, "get_transaction_sell_list", [user_id])

    transaction_sell_list = []
    transaction_sell_count = 0
    for transaction_id in sell_res[0]:
        res = client.call(contract_address, contract_abi, "get_transaction_info", [transaction_id])
        transaction_info = {
            "user_id_sell": res[1],
            "user_id_buy": res[2],
            "desc": res[3],
            "commodity_id": res[4],
            "price": res[5],
            "state": res[6],
            "id": transaction_id,
        }
        ret_code = 0 if transaction_info["state"] != -999 else -1
        if ret_code == 0:
            transaction_sell_list.append(transaction_info)
            transaction_sell_count += 1

    client.finish()

    if max_item_count is None:
        page_num = 1 if len(transaction_sell_list) > 0 else 0
    else:
        page_num = (len(transaction_sell_list) + max_item_count - 1) // max_item_count
        transaction_sell_list = transaction_sell_list[page_id * max_item_count: (page_id + 1) * max_item_count]


    return JsonResponse({
        "transaction_list": transaction_sell_list,
        "page_num": page_num,
    })

def buy_commodity(request):
    user_id = request.POST.get('user_id')
    commodity_id = int(request.POST.get('commodity_id'))

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "buy_commodity", [user_id, commodity_id, ""])
    txhash = receipt['transactionHash']
    txresponse = client.getTransactionByHash(txhash)
    inputresult = data_parser.parse_transaction_input(txresponse['input'])
    res = data_parser.parse_receipt_output(inputresult['name'], receipt['output'])
    client.finish()

    code_map = {
        0: 0,  # success 
        -1: -1,  # user state error
        -2: -2,  # commodity state error
        -3: -3,  # no enough money
        -4: -4,  # unable to change owner of commodity
        -5: -5,  # ubable to generate transaction
    }
    ret_code = code_map[res[0]]

    return JsonResponse({"code": ret_code})



def initiate_arbitration(request):
    user_id = request.POST.get('user_id')
    transaction_id = int(request.POST.get('transaction_id'))
    arbitration_reason = request.POST.get('arbitration_reason')

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "initiate_arbitration", [user_id, transaction_id, arbitration_reason])
    print(receipt)
    txhash = receipt['transactionHash']
    txresponse = client.getTransactionByHash(txhash)
    inputresult = data_parser.parse_transaction_input(txresponse['input'])
    res = data_parser.parse_receipt_output(inputresult['name'], receipt['output'])
    client.finish()
    print("---res:", res)
    code_map = {
        0: 0,  # success 
        -1: -1,  # user state error
        -2: -2,  # no such transaction
        -3: -3,  # unable to change state
        -4: -4,  # arbitration timeout
        -5: -5,  # unknown error
    }
    ret_code = code_map[res[0]]
    
    return JsonResponse({"code": ret_code})

def deal_arbitration(request):
    transaction_id = int(request.POST.get('transaction_id'))
    arbitration_valid = int(request.POST.get('arbitration_valid'))
    
    contract_name = "Admin"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "deal_arbitration", [transaction_id, arbitration_valid])
    txhash = receipt['transactionHash']
    txresponse = client.getTransactionByHash(txhash)
    inputresult = data_parser.parse_transaction_input(txresponse['input'])
    res = data_parser.parse_receipt_output(inputresult['name'], receipt['output'])
    client.finish()

    code_map = {
        0: 0,  # success
        -1: -1,  # no such transaction
        -2: -2,  # unable to undo transaction
        -3: -3,  # unable to change transaction state
        -4: -4,  # unable to change commodity state
    }
    ret_code = code_map[res[0]]

    return JsonResponse({"code": ret_code})