from fastapi import APIRouter,HTTPException,Depends,Form
from fastapi.requests import Request
from sqlalchemy.orm import Session
from models.DataBase import Supplier,Supplyrequest,Stock,Supplyrequest,Message
from models.Bridge import get_session
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from server.server_utils import *
supplier_router=APIRouter()
from fastapi.responses import RedirectResponse
templates=Jinja2Templates(directory="../frontend/Pharmacist")








########################## Login/Register/Dashboar ###############################################




@supplier_router.get("/login")
def login_template(request:Request):
    try:
        return templates.TemplateResponse(
            request=request,
            name="LoginTemaplate.html",
        )
    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)


@supplier_router.get("/register")
def Register_tempalte(request:Request):
    try:
        return templates.TemplateResponse(
            request=request,
            name="RegisterTemplate.html"
        )
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")





@supplier_router.post("/register")
def register(request:Request,db:Session=Depends(get_session),first_name=Form(...),last_name=Form(...),email=Form(...),
             password=Form(...),phone_number=Form(...),adress=Form(...)
             ):
    try:
        new_supplier=Supplier(
            first_name,last_name,email,password,phone_number,adress
        )
        db.add(new_supplier)
        db.refresh(new_supplier)
        db.commit()
        return RedirectResponse(
            url="/supplier/login",
            status_code=303
        )
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="RegisterTemplate.html",
            context={
                "Error_Message":f"Error {e} "
            }
        )

@supplier_router.post("/login")
def login(request:Request,db:Session=Depends(get_session),email=Form(...),password=Form(...)):
    try:
        user=db.query(Supplier).filter(Supplier.email==email).first()
        if user:
            if verify_password(password,user.password):
                token=create_token({"user_id":user.id,"email":user.email})
                reponse=RedirectResponse(
                    url="/supplier/dashboard",
                    status_code=303
                )
                reponse.set_cookie(
                    key="access_token",
                    token,
                    httponly=True,
                    secure=True
                )
                return reponse
            else:

                templates.TemplateResponse(
                    request=request,
                    name="LoginTemplate.html",
                    context={
                        "Error_Message":"Invalid Password"
                    }
                )

        else:
            return templates.TemplateResponse(
                request=request,
                name="LoginTemplate.html",
                context={
                    "Error_Message":"Invalid Email"
                }
            )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")


@supplier_router.get("/dashboard")
def dashboard(request:Request,supplier=Depends(get_current_Supplier)):
    stock=supplier.stock
    messages=supplier.messages
    requests=supplier.requests

    return templates.TemplateResponse(
        request=request,
        name="DashboardTemplate.html",
        context={
            "supplier":supplier,
            "stock_length":len(stock),
            "messages_lenght":len(messages),
            "requests_length":len(requests)
            }

    )



@supplier_router.get("/logout")
def logout(request:Request,supplier=Depends(get_current_Supplier)):
    return templates.TemplateResponse(
        request=request,
        name="LoginTemplate.html"
    )



 ################################## stocks #######################################


@supplier_router.get("/add_stock")
def add_stock_template(request:Request,supplier=Depends(get_current_Supplier)):
    try:
        return templates.TemplateResponse(
            request=request,
            name="AddStockTemplate.html",
        )
    except Exception as e:
        raise HTTPException(detail=f"Server Error:{e}",status_code=400)



@supplier_router.post("/add_stock")
def add_stock(request:Request,db:Session=Depends(get_session),supplier=Depends(get_current_Supplier),
                name=Form(...),reference=Form(...),cost_price=Form(...),quantity=Form(...),date=Form(...)
                ):
    try:
        new_stock=Stock(
            product_name=name,
            cost_price=cost_price,
            reference=reference,
            quantity=quantity,
            expiration_date=date,
            supplier_id=supplier.id
        )
        db.add(new_stock)
        db.refresh(new_stock)
        db.commit()

        stocks=supplier.stock
        return templates.TemplateResponse(
            request=request,
            name="StocksTemplate.html",
            context={
                "stocks":stocks,
                "message":"New stock added successfully"
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="AddStockTemplate.html",
            context={"Error_message":f"Error {e} while adding product"}
        )



@supplier_router.get("/stocks")
def stock(request:Request,supplier=Depends(get_current_Supplier)):
    try:
        return templates.TemplateResponse(
            request=request,
            name="StockTemplate.html",
            context={
                "stocks":supplier.stock
            }

        )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")



@supplier_router.get("/low_stocks")
def low_stock(request:Request,supplier=Depends(get_current_Supplier)):
    try:

        low_stock=[
            stock for stock in supplier.stock if stock.quantity<10
        ]

        return templates.TemplateResponse(
            request=request,
            name="LowStockTemaplate.html",
            context={
                "low_stock":low_stock
            }
        )



    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")



@supplier_router.get("/alert_products")
def alert_stock(request:Request,supplier=Depends(get_current_Supplier)):
    try:
        alert_products=[stock for stock in supplier.stock if  (datetime.today()-datetime.strptime(stock.expiration_date,"")).days<30]

        return templates.TemplateResponse(
            request=request,
            name="AlertProductsTemplate.html",
            context={
                "products":alert_products
            }
        )

    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)





############################### Requests ###################################################

@supplier_router.post("/validate_request")
def validate_request(request:Request,supply_id:int,supplier=Depends(get_current_Supplier),db:Session=Depends(get_session)):
    try:
        request=db.query(Supplyrequest).filter(Supplyrequest.id==supply_id).first()
        request.status="Valid"
        db.commit()
        return {
                "Message":"Request validated successfully"
            }
    except Exception as e:
        return {
            "Message":f"Error {e} validated the message "
        }
       

@supplier_router.get("/refuse_request")
def refuse_request(request:Request,request_id:int,bd:Session=Depends(get_session),supplier=Depends(get_current_Pharmacist)):
    try:
        request=bd.query(Supplyrequest).filter(Supplyrequest.id==request_id).first()
        request.status="Refused"
        bd.commit()
        return {
                "Message":"Request refused successfully"
            }
    except Exception as e:
        return {
            "Message":f"Error {e} refusing the message "
        }
       


@supplier_router.delete("/delete_request")
def delete_request(request_id:int,db:Session=Depends(get_current_Supplier)):
    try:
        request=db.query(Supplyrequest).filter(Supplyrequest.id==request_id).first()
        db.delete(request)
        db.commit()
        return {
                "Message":"Request deleted successfully"
            }
    except Exception as e:
        return {
            "Message":f"Error {e} deleting the message "
        }
       



@supplier_router.get("/requests")
def get_requests(request:Request,supplier=Depends(get_current_Supplier)):
    try:
        return templates.TemplateResponse(
            request=request,
            name="StockTemplate.html",
            context={
                "requests":supplier.supplies
            }
        )




    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)




############################## messages ##################################################



@supplier_router.post("/message_form")
def message_form(request:Request,supplier=Depends(get_current_Supplier)):
    try:
        return templates.TemplateResponse(
            request=request,
            name="AddMessageTemplate.html"
        )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error : {e}")



@supplier_router.post("/send_message")
def send_message(request:Request,pharmacist_id:int,content:str=Form(...),object:str=Form(...),
                 supplier=Depends(get_current_Supplier),db:Session=Depends(get_session)):

    try:
        receiver=db.query(Pharmacist).filter(Pharmacist.id==pharmacist_id).first()
        if receiver:
            new_message=Message(
                object=object,
                message_content=content,
                supplier_id=supplier.id,
                pharmacist_id=pharmacist_id,
            )
            db.add(new_message)
            db.commit()
            return templates.TemplateResponse(
                request=request,
                name="MessagesTemplate.html",
                context={
                    "message":"Message added succesfully"
                }
            )
        else:
            return templates.TemplateResponse(
                request=request,
                name="AddMessageTemplate.html",
                context={
                    "message":"Invalid Email"
                }
            )



    except Exception as e:
        raise HTTPException(status_code=400,detail=F"Server Error: {e}")




@supplier_router.get("/messages")
def get_messages(request:Request,supplier=Depends(get_current_Supplier)):
    try:

        messages=supplier.messages
        return templates.TemplateResponse(
            request=request,
            name="MessagesTemplate.html",
            context={
                "messages":messages
            }
        )

    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)









