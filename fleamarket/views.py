from django.shortcuts import render
from django.http import JsonResponse

from client.contractnote import ContractNote
from client.datatype_parser import DatatypeParser
from client.bcosclient import BcosClient

# Create your views here.

def create_user(request):
    user_name = request.POST.get('user_name')
    user_password = request.POST.get('user_password')
    balance = int(request.POST.get('balance'))
    info = ""

    contract_name = "Admin"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.sendRawTransaction(contract_address, contract_abi, "create_user", [user_name, user_password, balance, info])
    client.finish()
    
    return JsonResponse({"code": res[0]})


def auth_user(request):
    user_id = request.POST.get('user_id')
    user_password = request.POST.get('user_password')

    contract_name = "Admin"

def market_commodity_list(request):
    # TODO: wait for block chain interface update
    pass

def user_commodity_list(request):
    user_id = request.POST.get('user_id')

    # TODO: wait for block chain interface update
    

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
    res = client.sendRawTransaction(contract_address, contract_abi, "create_commodity", [user_id, commodity_name, commodity_image, commodity_desc])
    client.finish()

    return JsonResponse({"code": res[0]})


def up_commodity(request):
    user_id = request.POST.get('user_id')
    user_password = request.POST.get('user_password')
    commodity_id = request.POST.get('commodity_id')

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.sendRawTransaction(contract_address, contract_abi, "puton_commodity", [user_id, user_password, commodity_id])
    client.finish()

    return JsonResponse({"code": res[0]})

def down_commodity(request):
    user_id = request.POST.get('user_id')
    user_password = request.POST.get('user_password')
    commodity_id = request.POST.get('commodity_id')

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.sendRawTransaction(contract_address, contract_abi, "putdown_commodity", [user_id, user_password, commodity_id])
    client.finish()

    return JsonResponse({"code": res[0]})

def user_transaction_list(request):
    user_id = request.POST.get('user_id')

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "get_transaction_buy_list", [user_id])
    client.finish()

    return JsonResponse({
        "transactions": res[0],
        "transaction_count": res[1],
    })
    

def buy_commodity(request):
    user_id = request.POST.get('user_id')
    user_password = request.POST.get('user_password')
    commodity_id = request.POST.get('commodity_id')

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.sendRawTransaction(contract_address, contract_abi, "buy_commodity", [user_id, user_password, commodity_id, ""])
    client.finish()

    return JsonResponse({"code": res[0]})



def initiate_arbitration(request):
    user_id_from = request.POST.get('user_id_from')
    #user_id_to = request.POST.get('user_id_to')
    transaction_id = request.POST.get('transaction_id')

    contract_name = "User"
    contract_address = ContractNote.get_last(contract_name)

    abi_file = f"contracts/{contract_name}.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi

    client = BcosClient()
    res = client.call(contract_address, contract_abi, "initiate_arbitration", [user_id_from, transaction_id])
    client.finish()

    return JsonResponse({"code": res[0]})