# composite-service
# This service will act as a gateway and call the other 3 microservices

Design:
1. Front end needs to connect to this new Composite Service
2. Composite Service will not handle CRUD, it will call the User Service which will then authenticate user, get trip details, etc
3. User Service needs to be changed such that it does not directly call itinerary service (Composite->User, User->Composite, then Composite->Itinerary)
4. User Service data obtained must be sent back to Composite Service (trip id, all trip info, etc) 
5. Composite Service will pass in trip info and complete CRUD regarding flight details on Itinerary Service
6. Details from Itinerary Service need to be passed back to composite(the destination city), and composite will call review
7. Review service called from Composite once user clicks save from Review Tab, so that the user can review the destination city

Composite MS Requirements:
https://github.com/donald-f-ferguson/Topics-in-SW-Engineering-F22/blob/main/docs/Project-Sprints/README-Sprint-2.md 
