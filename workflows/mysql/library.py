'''
MySQL connectivity library.

@author: Anze Vavpetic <anze.vavpetic@ijs.si>
'''
import os
import tempfile
import time
from context import DBConnection, DBContext, MySqlDAL, PgSqlDAL
from converters import RSD_Converter, Aleph_Converter, Orange_Converter, TreeLikerConverter, PrdFctConverter
from mapper import domain_map

def database_connect(input_dict):
    user = str(input_dict['user'])
    password = str(input_dict['password'])
    host = str(input_dict['host'])
    db = str(input_dict['database'])
    dal = None
    
    if str(input_dict['vendor']) == 'mysql':
        dal = MySqlDAL()
    else:
        dal = PgSqlDAL()
    
    con = DBConnection(user, password, host, db, dal)
    return {'connection' : con}

def mysql_db_context(input_dict):
    return {'context' : None}

def mysql_db_context_finished(postdata, input_dict, output_dict):
    con = input_dict['connection']
    find_con = input_dict['find_connections'] == 'true'
    context = DBContext(con, find_connections=find_con)
    context.update(postdata)
    return {'context' : context}

def mysql_rsd_converter(input_dict):
    dump = input_dict['dump'] == 'true'
    rsd = RSD_Converter(input_dict['context'], discr_intervals=input_dict['discr_intervals'] or {})
    return {'examples' : rsd.all_examples(), 'bk' : rsd.background_knowledge()}

def mysql_aleph_converter(input_dict):
    dump = input_dict['dump'] == 'true'
    target_att_val = input_dict['target_att_val']
    if not target_att_val:
        raise Exception('Please specify a target attribute value.')
    aleph = Aleph_Converter(input_dict['context'], target_att_val=target_att_val, discr_intervals=input_dict['discr_intervals'] or {})
    return {'pos_examples' : aleph.positive_examples(), 'neg_examples' : aleph.negative_examples(), 'bk' : aleph.background_knowledge()}

def mysql_treeliker_converter(input_dict):
    treeliker = TreeLikerConverter(input_dict['context'], 
                                   discr_intervals=input_dict['discr_intervals'] or {})
    return {'dataset': treeliker.dataset(), 
            'template': treeliker.default_template()}

def mysql_query_to_odt(input_dict):
    return {'dataset' : None}

def mysql_orange_converter(input_dict):
    context = input_dict['context']
    orange = Orange_Converter(context)
    return {'target_table_dataset' : orange.target_Orange_table(),'other_table_datasets': orange.other_Orange_tables()}

def mysql_prd_fct_converter(input_dict):   
    context = input_dict['context']
    prd_fct = PrdFctConverter(context)
    

    #progress bar issue
    url=os.path.dirname(os.path.abspath(__file__))
    url=os.path.normpath(os.path.join(url,'..','..','mothra','public','files'))
    #if not os.path.exists(url):
    #    os.makedirs(url)  
    #url=os.path.normpath(os.path.join(url,str(widget.workflow_id)))
    #if not os.path.exists(url):
    #    os.makedirs(url)

    url = tempfile.mkdtemp(dir=url)
    timenow = int(round(time.time() * 1000))
    prd_file_url=os.path.join(url,"prdFctTemp%s.prd"%str(timenow))
    with open(prd_file_url, "w") as prd:
        prd.write( prd_fct.create_prd_file());   

    fct_file_url=os.path.join(url,"prdFctTemp%s.fct"%str(timenow))
    with open(fct_file_url, "w") as fct:
        fct.write( prd_fct.create_fct_file());      

    return {'prd_file' : prd_file_url,'fct_file': fct_file_url}

def ilp_map_rsd(input_dict):
    return do_map(input_dict, 'rsd')

def ilp_map_treeliker(input_dict):
    return do_map(input_dict, 'treeliker')

def ilp_map_aleph(input_dict):
    positive_class = input_dict['positive_class']
    return do_map(input_dict, 'aleph', positive_class=positive_class)

def do_map(input_dict, feature_format, positive_class=None):
    '''
    Maps a new example to a set of features.
    '''
    # Context of the unseen example(s)
    train_context = input_dict['train_ctx']
    test_context = input_dict['test_ctx']

    # Currently known examples & background knowledge
    features = input_dict['features']
    format = input_dict['output_format']

    evaluations = domain_map(features, feature_format, train_context,
                             test_context, format=format,
                             positive_class=positive_class)
    return {'evaluations' : evaluations}
