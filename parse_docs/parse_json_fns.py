import glob
import re
from LazyScripts.LazyJSON import read_json

# string to format for GET methods
GET_METHOD_STR = '''
    @BaseAPI._memoize
    def {0}(self, {1}):
        """{2}
        {3} method

        Args:
            REQUIRED:
            {4}
            Optional:
            {5}

        Returns JSON of response.
        """
        {8}

        params = self._parse_params(locals().copy(), {7})
        query_string = '{6}?' + params

        return self._get(query_string)'''
# string to format for POST/DELETE methods
POST_METHOD_STR = '''
    def {0}(self, {1}):
        """{2}
        {3} method

        Args:
            REQUIRED:
            {4}
            Optional:
            {5}

        Returns JSON of response.
        """
        {8}

        payload = self._parse_payload(locals().copy(), {7})
        endpoint = '{6}'  + self._param('hm_token', self.hm_token)

        return self._post(endpoint, payload)'''
# page/count params are not always included when they are supported;
# their metadata is here to be referenced
PAGE_PARAM = {'required': False, 'allowMultiple': False, 'name': 'page',
              'paramType': 'query', 'dataType': 'int',
              'description': 'the page of the collection'}
COUNT_PARAM = {'required': False, 'allowMultiple': False, 'name': 'count',
               'paramType': 'query', 'description': 'items per page',
               'dataType': 'int'}
ENDPOINT_ARG_REGEX = r'{(\w*)}'  # used to parse endpoint-specific args
DEFAULT_ARG_REGEX = r"\(default is '(\w*)'"
# for indentation-level-formatting:
# new line, two tabs
NL2T = '\n        '
# new line, three tabs
NL3T = '\n            '
REQUIRE_HM_TOKEN = """hm_token = self._assert_hm_token(hm_token)"""


def parse_all_docs():
    '''Creates method-strings for all endpoint categories
    (user, blogs, tracks, etc)
    Returns a string'''
    methods = []
    for doc in glob.glob('raw_docs/*.json'):
        doc_json = read_json(doc)
        # this is just how hypem breaks it up
        methods.append("\n    ''' " + doc_json['resourcePath'] + " '''")
        for api_doc in doc_json['apis']:
            methods += format_api(api_doc)
    # join them all together with newlines
    return '\n'.join(methods)


def format_api(api_doc):
    '''Creates method-strings for all operations in an api endpoint.
    Returns a list of method-strings.
    Args:
        dict api_doc: documentation for a specific endpoint-family
            (hypem provides category > api > operations > [])
    '''
    api_methods = []
    resource_path = api_doc['path']
    # take note of which are not actually part of get/post payload
    endpoint_args = re.findall(ENDPOINT_ARG_REGEX, resource_path)
    # split out {endpoint} names as variables, eg
    # /{artist}/ becomes '/' + str(artist) + '/'
    resource_path = resource_path.replace("{", "' + str(") \
        .replace("}", ") + '")
    for operation in api_doc['operations']:
        op_method = format_operation(resource_path, operation,
                                     endpoint_args)
        api_methods.append(op_method)
    return api_methods


def format_operation(resource_path, operation, endpoint_args):
    '''Returns method-string for a specific operation given a resource path

    Args:
        string resource_path: the endpoint to the path
        dict operation: dictionary of documentation for the given operation
        list endpoint_args: list of args that are part of the resource_path,
            which should not be part of payload

    '''
    # types and descriptions for required parameters
    required_docstrings = []
    optional_docstrings = []
    # actual method args + default parameters
    required_params = []
    optional_params = []
    # assertion statements as necessary
    assertions = []
    # keep track if not paginated by default, to add optional page/count
    # parameters afterward
    not_paginated = 'Not paginated' in operation.get('notes', '')
    seen_params = set()

    # iterate over params, and generate docstrings and method arg strings
    for param in operation['parameters']:
        seen_params.add(param['name'])
        parse_param(param, required_docstrings, optional_docstrings,
                    required_params, optional_params, assertions)
    # if page/count aren't in seen params, but endpoint
    # allows pagination, prepend the page/count params to the list
    # (checking for 'page' should be sufficient)
    if not_paginated and 'page' not in seen_params:
        for param in [COUNT_PARAM, PAGE_PARAM]:
            parse_param(param, required_docstrings, optional_docstrings,
                        required_params, optional_params, assertions)

    # list of elements used to format docstring
    # (I like this because it's enumerated in the same way as the
    # format string)
    format_list = [''] * 9
    format_list[0] = operation['nickname']
    format_list[1] = ', '.join(required_params + optional_params)
    format_list[2] = NL2T.join([operation['summary'],
                                operation.get('notes', '')])
    format_list[3] = operation['httpMethod']
    format_list[4] = NL3T.join(required_docstrings)
    format_list[5] = NL3T.join(optional_docstrings)
    format_list[6] = resource_path
    format_list[7] = endpoint_args
    if 'hm_token=None' in required_params:
        format_list[8] = REQUIRE_HM_TOKEN
    if assertions:
        format_list[8] += '\n'.join(assertions)
    if operation['httpMethod'] == 'GET':
        return GET_METHOD_STR.format(*format_list)
    else:
        return POST_METHOD_STR.format(*format_list)


def parse_param(param, rdoc, odoc, rparam, oparam, asserts):
    '''Parse docstrings and argument defaults from a parameter
    Args:
        dict param: a dict of parameter information
        list rdoc: list of other required docstrings
        list odoc: list of other optional docstrings
        list rparam: list of other required parameters
        list oparam: list of other optional parameters
    Lists passed by reference are modified in their original scope'''
    # param passed as arg to method
    param_arg = param['name']
    # info about param in docstring
    param_docstring = '- ' + param['dataType'] + ' ' + \
        param['name'] + ': ' + param['description']
    default_val = re.findall(DEFAULT_ARG_REGEX, param['description'])
    if default_val:
        param_arg += "='" + str(default_val[0]) + "'"
    # check for allowable values
    if param.get('allowableValues'):
        allowable = param.get('allowableValues').get('values')
        allowable = [str(x) for x in allowable]  # cast as str
        asserts.append(parse_assertion(param['name'], allowable))
        param_docstring += NL3T + '    allowable values: '
        param_docstring += ', '.join(allowable)
    if param['required']:
        if param_arg == 'hm_token':
            param_arg += '=None'
        rparam.append(param_arg)
        rdoc.append(param_docstring)
    else:
        # if there is no default value
        if '=' not in param_arg:
            # set default of optional params to None
            param_arg += '=None'
        oparam.append(param_arg)
        odoc.append(param_docstring)

def parse_assertion(param_name, allowed_values):
    '''Generates an assert statement for when a parameter has specific allowed
    values.

    Args:
        string param_name: name of the parameter
        list allowed_values: list of allowed values (coerced to str)'''
    or_str = ' or '.join(allowed_values)
    statement = NL2T + """assert str({0}) in {1}, '"{0}" must be {2}'""".format(param_name,
        allowed_values, or_str)
    return statement

if __name__ == '__main__':
    print(parse_all_docs())
