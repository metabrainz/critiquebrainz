Publication Endpoints
=====================

## /publication/:id:

    Fetch publication
    
    Methods:
    * GET
    
    Parameters:
    * inc (optional)
    
    Returns:
    * publication
    
## /publication/:id:

    REQUIRES AUTHORIZATION
    Update publication
    
    Methods:
    * PUT
    
    Parameters:
    * text
    
## /publication/:id:

    REQUIRES AUTHORIZATION
    Delete publication
    
    Methods:
    * Delete
    
## /publication/

    REQUIRES AUTHORIZATION
    Post publication
    
    Methods:
    * POST
    
    Parameters:
    * text
    
## /publication/

    Browse publications
    
    Methods:
    * GET
    
    Parameters:
    * release_group (optional if user_id is set)
	* user_id (optional if release_group is set)
	* limit (optional)
	* offset (optional)
	* rating (optional)
	* inc (optional)


OAuth Endpoints
===============

## /oauth/authorize
	
	REQUIRES AUTHORIZATION
	Generates authorization code.

    Methods:
    * POST
    
	Parameters:
	* client_id
	* response_type
	* redirect_uri
	* scope
	* state (optional)

	Returns:
	* authorization code

## /oauth/token

	Generates access token from authorization code or refresh token.

    Methods:
    * POST
    
	Parameters:
	* grant_type
	* code OR access_token
	* redirect_uri (optional if grant_type is 'refresh_token')
	* client_id
    * client_secret

	Returns:
    * token type
	* access token
	* refresh token
	* expiration time

## /oauth/get_client

	Validates authorization request parameters and returns client-related data.

	Parameters:
	* client_id
	* response_type
	* redirect_uri
	* scope

	Returns:
	* client data

## /oauth/login/:provider:

	Redirects to provider login form

	Parameters:
	* client_id
	* response_type
	* redirect_uri
	* scope
	* state (optional)

	Redirects to:
	* provider login form

## /oauth/login/:provider:/post

    Redirect to:
    * client redirect_uri with authorization code
    

