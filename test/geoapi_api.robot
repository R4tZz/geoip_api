*** Settings ***
Documentation  API Testing in Robot Framework
Library  SeleniumLibrary
Library  RequestsLibrary
Library  JSONLibrary
# Library  Collections

*** Variables ***
${API_URL}   http://localhost:8000/
## Test Data:
${username}  username1
${email}  email1
${password}  password1
${IP_TO_TEST}  172.253.62.94

*** Test Cases ***
Request Register
    [documentation]  Request Register test case:
    ...  Target API URL: http://localhost:8000/auth/register
    ...  Perform Post request
    ...  Expected status code: 201 or 409
    [tags]  Smoke
    Create Session  mysession  ${API_URL}  verify=true
    &{header}=  Create Dictionary  Content-Type=application/json   accept=application/json
    ${json}=  Convert String to JSON  {"username": "${username}","email": "${email}","password": "${password}","confirm_password": "${password}"}
    ${response}=  POST On Session  mysession  /auth/register  json=${json}  headers=${header}  expected_status=any
    Log     ${response.text}
    Log     ${response.status_code}
    Should Be True  ${response.status_code}==201 or ${response.status_code}==409

Request Login
    [documentation]  Request Login test case:
    ...  Target API URL: http://localhost:8000/auth/login
    ...  Perform Post request
    ...  Expected status code: 200
    ...  Set Token as global variable
    [tags]  Smoke
    Create Session  mysession  ${API_URL}  verify=true
    &{body}=  Create Dictionary  grant_type=  username=${username}  password=${password}  scope=  client_id=  client_secret=
    &{header}=  Create Dictionary  Content-Type=application/x-www-form-urlencoded   accept=application/json
    ${response}=  POST On Session  mysession  /auth/login  data=${body}  headers=${header}
    Status Should Be  200  ${response}
    ${token_string} =   Convert String to JSON  ${response.text}
    ${token}=  Get Value From Json	${token_string}  $.."access_token"
    Set Global Variable   ${token}
    Log   ${token}

Request Get IP Location
    [documentation]  Request Get IP Location test case:
    ...  Target API URL: http://localhost:8000/auth/location/ip_url/{ip_url}
    ...  Perform Get request using a jwt token
    ...  Expected status code: 200
    [tags]  Smoke
    Create Session  mysession  ${API_URL}  verify=true
    &{header}=  Create Dictionary  Authorization=Bearer ${token}[0]  accept=application/json
    ${response}=  GET On Session  mysession  /location/ip_url/${IP_TO_TEST}  headers=${header}
    Status Should Be  200  ${response}
    Log  ${response.text}

Request Add IP Location
    [documentation]  Request Add IP Location test case:
    ...  Target API URL: http://localhost:8000/auth/location/ip_url/{ip_url}
    ...  Perform Put request using a jwt token
    ...  Expected status code: 201
    [tags]  Smoke
    Create Session  mysession  ${API_URL}  verify=true
    &{header}=  Create Dictionary  Authorization=Bearer ${token}[0]  accept=application/json
    ${response}=  PUT On Session  mysession  /location/ip_url/${IP_TO_TEST}  headers=${header}
    Status Should Be  201  ${response}
    Log  ${response.text}

Request Delete IP Location
    [documentation]  Request Delete IP Location test case:
    ...  Target API URL: http://localhost:8000/auth/location/ip_url/{ip_url}
    ...  Perform Delete request using a jwt token
    ...  Expected status code: 200
    [tags]  Smoke
    Create Session  mysession  ${API_URL}  verify=true
    &{header}=  Create Dictionary  Authorization=Bearer ${token}[0]  accept=application/json
    ${response}=  DELETE On Session  mysession  /location/ip_url/${IP_TO_TEST}  headers=${header}
    Status Should Be  200  ${response}
    Log  ${response.text}


*** Keywords ***
