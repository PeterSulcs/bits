import json
import datetime
import time

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

import markdown

from utils import (
    get_actions,
    get_user_projects,
    get_project,
    get_tickets,
    get_ticket,
    get_comments,
)

from .models import (
    DBSession,
    UserTypes,
    Users,
    LoginTokens,
    Organizations,
    UserOrganizationAssignments,
    Projects,
    UserProjectAssignments,
    TicketTypes,
    TicketPriorities,
    Tickets,
    TicketComments,
    RequirementTypes,
    Requirements,
    RequirementComments,
    Actions,
)

def make_response(resp_dict):

    print "[DEBUG]"
    print resp_dict
    print '\n'
    
    resp = Response(json.dumps(resp_dict), content_type='application/json', charset='utf8')
    resp.headerlist.append(('Access-Control-Allow-Origin', '*'))
    
    return resp

def check_auth(token):
    
    user = LoginTokens.check_authentication(
        session = DBSession,
        token = token,
    )
    return user

@view_config(route_name='login', renderer='templates/login.mak')
def login(request):

    return {}

@view_config(route_name='index', renderer='templates/index.mak')
def index(request):

    result = {}
    if True:
    #try:

        result['user'] = None
        result['token'] = None

        token = request.cookies['token']
        user = check_auth(token)
        if user == None:
            raise Exception('invalid token')

        result['user'] = user
        result['token'] = token

        result['projects'] = get_user_projects(user)

        result['actions'] = get_actions(user, limit=25)


    #except:
    #    pass

    return result #{'token': token, 'user': user, 'projects': projects}

@view_config(route_name='project', renderer='templates/project.mak')
def project(request):

    result = {}
    if True:
    #try:
        result['user'] = None
        result['token'] = None

        token = request.cookies['token']
        user = check_auth(token)
        if user == None:
            raise Exception('invalid token')

        result['user'] = user
        result['token'] = token

        project_id = request.GET['project_id']
            
        result['project'] = get_project(user, project_id)

        result['tickets'] = get_tickets(project_id)

    #except:
    #    pass

    return result

@view_config(route_name='ticket', renderer='templates/ticket.mak')
def ticket(request):

    result = {}
    if True:
    #try:

        result['user'] = None
        result['token'] = None

        token = request.cookies['token']
        user = check_auth(token)
        if user == None:
            raise Exception('invalid token')

        result['user'] = user
        result['token'] = token

        ticket_id = request.GET['ticket_id']
        #project_id = request.GET['project_id']

        print "\n\nticket: Ticket ID:"
        print ticket_id
        print "\n\n"

        ticket = get_ticket(ticket_id)
        result['ticket'] = ticket

        print "\n\nticket: Ticket:"
        print ticket
        print "\n\n"

        result['comments'] = get_comments(ticket['id'])

        result['tickets'] = get_tickets(ticket['project_id'])

        result['project'] = get_project(user, ticket['project_id'])

    #except:
    #    pass

    return result #{'ticket': None, 'user': user, 'token': token, 'project': None}

@view_config(route_name='newticket', renderer='templates/newticket.mak')
def new_ticket(request):

    result = {}
    if True:
    #try:

        result['user'] = None
        result['token'] = None

        token = request.cookies['token']
        user = check_auth(token)
        if user == None:
            raise Exception('invalid token')

        result['user'] = user
        result['token'] = token

        project_id = request.GET['project_id']

        result['project'] = get_project(user, project_id)
   
        result['tickets'] = get_tickets(project_id)
 
    #except:
    #    pass

    return result

@view_config(route_name='newproject', renderer='templates/newproject.mak')
def new_project(request):

   
    result = {}
    #if True:
    try:

        result['user'] = None
        result['token'] = None

        token = request.cookies['token']
        user = check_auth(token)
        if user == None:
            raise Exception('invalid token')

        result['user'] = user
        result['token'] = token

        raw_projects = Projects.get_projects_from_user_id(
            session = DBSession,
            user_id = user.id,
        )

        projects = []
        for upa_id, upa_disabled, p_id, p_name, p_desc, p_created, \
                p_disabled, o_first, o_last, o_email, r_count, t_count \
                in raw_projects:
            if upa_disabled == False and p_disabled == False:
                projects.append({
                    'id': p_id,
                    'name': p_name,
                    'description': p_desc,
                    'created': p_created.strftime("%b %d, %Y"),
                    'owner': '{0} {1}'.format(o_first, o_last),
                    'owner_email': o_email,
                    'requirement_count': r_count,
                    'ticket_count': t_count,
                    'note_count': 0,
                })

        result['projects'] = projects;

    except:
        pass

    return result
 

@view_config(route_name='authenticate.json')
def authenticate(request):

    """ End-point to authenticate user, and return a login token
    """

    result = {}
    result['success'] = False
    #if True:
    try:
        try:
            email = request.GET['email']
            password = request.GET['password']
        except:
            result['error_text'] = 'Missing Field'
            result['error_code'] = 1
            raise Exception('error')

        user, token = LoginTokens.do_login(
            session = DBSession,
            email = email,
            password = password,
        )

        if token == None:
            result['error_text'] = 'Invalid Credentials'
            result['error_code'] = 2
            raise Exception('error')

        user_type = UserTypes.user_type_from_id(
            session = DBSession,
            user_type_id = user.user_type_id,
        )

        result['token'] = token
        result['user'] = {
            'first': user.first,
            'last': user.last,
            'email': user.email,
            'user_type': user_type.name,
            'user_type_description': user_type.description,
        }

        result['success'] = True

    except:
        pass

    return make_response(result)

@view_config(route_name='create_ticket.json')
def create_ticket(request):

    """ Create a new ticket
    """

    result = {}
    result['success'] = False

    if True:
    #try:

        #result['user'] = None
        #result['token'] = None

        token = request.cookies['token']
        user = check_auth(token)
        if user == None:
            raise Exception('invalid token')

        #result['user'] = user
        #result['token'] = token

        project_id = request.POST['project_id']
        title = request.POST['title']
        contents = request.POST['contents']
        ticket_type_id = 1 # request.POST['ticket_type_id']

        print "\n\ncreate_ticket: project_id: {0}\n\n".format(project_id)

        ticket = Tickets.add_ticket(
            session = DBSession,
            author_id = user.id,
            project_id = project_id,
            ticket_type_id = ticket_type_id,
            title = title,
            contents = contents,
            #ticket_priority_id = 1, #ticket_priority_id,
        )
        #ticket_contents = TicketContents.add_ticket_content(
        #    session = DBSession,
        #    author_id = user.id,
        #    ticket_id = ticket.id,
        #    title = title,
        #    contents = contents,
        #)

        result['ticket_id'] = ticket.id

        action = Actions.add_action(
            session = DBSession,
            organization_id = 1,
            user_id = user.id,
            action_type = "created",
            subject = "ticket",
            project_id = project_id,
            ticket_id = ticket.id,
            requirement_id = None,
        )


        result['success'] = True

    #except:
    #    pass

    return make_response(result)

@view_config(route_name='create_project.json')
def create_project(request):

    """ Create a new project
    """

    result = {}
    result['success'] = False

    #if True:
    try:

        #result['user'] = None
        #result['token'] = None

        token = request.cookies['token']
        user = check_auth(token)
        if user == None:
            raise Exception('invalid token')

        #result['user'] = user
        #result['token'] = token

        #project_id = request.POST['project_id']
        name = request.POST['name']
        description = request.POST['description']
        #ticket_type_id = 1 # request.POST['ticket_type_id']

        project = Projects.add_project(
            session = DBSession,
            author_id = user.id,
            organization_id = 1,
            name = name,
            description = description,
            #project_id = project_id,
            #ticket_type_id = ticket_type_id,
            #ticket_priority_id = 1, #ticket_priority_id,
        )

        assignment = UserProjectAssignments.assign_user_to_project(
            session = DBSession,
            user_id = user.id,
            project_id = project.id,
        )

        result['project_id'] = project.id

        action = Actions.add_action(
            session = DBSession,
            organization_id = 1,
            user_id = user.id,
            action_type = "created",
            subject = "project",
            project_id = project.id,
            ticket_id = None,
            requirement_id = None,
        )

        result['success'] = True

    except:
        pass

    return make_response(result)


@view_config(route_name='create_comment.json')
def create_comment(request):

    """ Get all of the organizations that the user has access to
    """

    result = {}
    result['success'] = False

    #if True:
    try:

        token = request.cookies['token']
        user = check_auth(token)
        if user == None:
            raise Exception('invalid token')

        #author_id = request.POST['author_id']
        #project_id = request.POST['project_id']
        ticket_id = request.POST['ticket_id']
        contents = request.POST['contents']

        ticket = Tickets.get_by_id(
            session = DBSession,
            ticket_id = ticket_id,
        )

        ticket_comment = TicketComments.add_ticket_comment(
            session = DBSession,
            author_id = user.id,
            ticket_id = ticket.id,
            contents = contents,
        )

        result['ticket_comment_id'] = ticket_comment.id

        action = Actions.add_action(
            session = DBSession,
            organization_id = 1,
            user_id = user.id,
            action_type = "created",
            subject = "comment",
            project_id = ticket.project_id,
            ticket_id = ticket_id,
            requirement_id = None,
        )

        result['success'] = True

    except:
        pass

    return make_response(result)

