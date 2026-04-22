
# API ARCHITECTURE

* Route file is the entry point for all the apis, 
  We will use route file for request and and response handling  
  In the route file we will call service function and only accept and return the response 
* Schemas are for validation of request and response structure
* we will write any busines logic and dbqueries in service


### steps to crete a api
 1. create a route file with that module name, naming convention - route_module.py
 2. create a response model in schema for response structure, but first create a Base response structure
 3. Now in the route's response_model wrap the specific model with in the base response
 4. now in the  route file call the service function and pass the required paramtere
 5. Do all the business logic  in service file.
 6. And db queries in the repository file

 Optional
 7. For common helper function we will create a file in helpers.helper.py 


dashboard/kpis
 Quote - 
 1. inquiry/list (where isquote form 0)
 2. quote/list (where isquote form 1)
 2. Add status coloms to enquiry table
 3. edit and view details api



 