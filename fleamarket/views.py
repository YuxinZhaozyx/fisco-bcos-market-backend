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
        "user_id_sell": res[0],
        "user_id_buy": res[1],
        "desc": res[2],
        "commodity_id": res[3],
        "price": res[4],
        "state": res[5],
        "id": transaction_id,
    }

    ret_code = 0 if transaction_info["state"] != -999 else -1
    response = {
        "code": ret_code,
    }
    if ret_code == 0:
        response["transaction"] = transaction_info

    return JsonResponse(response)



def market_commodity_list(request):
    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "get_onsale_list", [])

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
        }
        if commodity_info["state"] != -999:
            commodity_list.append(commodity_info)
    
    client.finish()
    

    return JsonResponse({"commodity_list": commodity_list})

def user_commodity_list(request):
    user_id = request.POST.get('user_id')

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
        }
        if commodity_info["state"] != -999:
            commodity_list.append(commodity_info)
    
    client.finish()

    return JsonResponse({"commodity_list": commodity_list})
    


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

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "puton_commodity", [user_id, commodity_id, commodity_price])
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

def user_transaction_list(request):
    user_id = request.POST.get('user_id')

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    sell_res = client.call(contract_address, contract_abi, "get_transaction_sell_list", [user_id])
    buy_res = client.call(contract_address, contract_abi, "get_transaction_buy_list", [user_id])

    transaction_sell_list = []
    transaction_sell_count = 0
    for transaction_id in sell_res[0]:
        res = client.call(contract_address, contract_abi, "get_transaction_info", [transaction_id])
        transaction_info = {
            "user_id_sell": res[0],
            "user_id_buy": res[1],
            "desc": res[2],
            "commodity_id": res[3],
            "price": res[4],
            "state": res[5],
            "id": transaction_id,
        }
        ret_code = 0 if transaction_info["state"] != -999 else -1
        if ret_code == 0:
            transaction_sell_list.append(transaction_info)
            transaction_sell_count += 1

    transaction_buy_list = []
    transaction_buy_count = 0
    for transaction_id in buy_res[0]:
        res = client.call(contract_address, contract_abi, "get_transaction_info", [transaction_id])
        transaction_info = {
            "user_id_sell": res[0],
            "user_id_buy": res[1],
            "desc": res[2],
            "commodity_id": res[3],
            "price": res[4],
            "state": res[5],
            "id": transaction_id,
        }
        ret_code = 0 if transaction_info["state"] != -999 else -1
        if ret_code == 0:
            transaction_buy_list.append(transaction_info)
            transaction_buy_count += 1

    client.finish()

    return JsonResponse({
        "transactions_sell": transaction_sell_list,
        "transaction_sell_count": transaction_sell_count,
        "transactions_buy": transaction_buy_list,
        "transaction_buy_count": transaction_buy_count,
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

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "initiate_arbitration", [user_id, transaction_id])
    client.finish()

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
    
    contract_name = "Admin"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    receipt = client.sendRawTransactionGetReceipt(contract_address, contract_abi, "deal_arbitration", [transaction_id])
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