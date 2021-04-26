from datetime import datetime


# checks whether the requested page number is valid
def get_page(page):
    if page is not None:
        if page.isnumeric():
            if int(page) > 0:
                return int(page)
    # default:
    return 1


# checks whether the requested per page value is valid
def get_per_page(per_page):
    if per_page is not None:
        if per_page.isnumeric():
            if int(per_page) > 0:
                return int(per_page)
    # default:
    return 10


# checks whether the requested order by value is valid
def get_order_by_sumbissions(order_by, whitelist):
    if order_by is not None:
        if order_by.lower() in whitelist:
            return order_by.lower()
    # default:
    return 'id'


# checks whether the requested order by value is valid
def get_order_companies(order_by, order_type, whitelist):
    if order_by is not None and order_by.lower() in whitelist:
        types = ['asc', 'desc']
        if order_type is not None and order_type.lower() in types:
            return ' ORDER BY ' + order_by.lower() + ' ' + order_type.lower()
        else:
            return ' ORDER BY ' + order_by.lower() + ' desc'
    # default:
    return ''


# checks whether the requested order type is valid
def get_order_type_submissions(order_type):
    whitelist = [
        'asc',
        'desc'
    ]

    if order_type is not None:
        if order_type.lower() in whitelist:
            return order_type
    # default:
    return 'desc'


# checks whether the requested date is in ISO 8601 format
def get_date(date):
    if date is not None:
        try:
            result = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except ValueError:
            return None  # not a valid date format
        return str(result)
    # not a valid date format
    return None


# chceks whether there is a search query and kkeps the format foll CIN field comparison
def get_query(query):
    if query is not None:
        return query
    return None


# chceks whether there is a search query and formats it for full text substring search
def get_substring_query(query):
    if query is not None:
        return '%' + query + '%'  # percent signs enable substring search
    return None


# creates the WHERE part of the SQL query based on input parameters
def construct_where_clause(params):
    sql = ''  # if no parameters are requested, the WHERE part will remain an empty string
    if len(params) > 0:
        sql += ' WHERE ' + params[0]
        index = 1
        # if there is more than one parameter, they get added with AND in between them
        while index < len(params):
            sql += ' AND ' + params[index]
            index += 1
    return sql
