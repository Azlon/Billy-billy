import plotly

plotly.tools.set_credentials_file(username='billy-billy', api_key='CvrH1saCD1wrq5Ye4II2')

username = 'billy-billy'
api_key = 'CvrH1saCD1wrq5Ye4II2'
stream_tokens = ['gmnwwr1zfx',
                 'bdg9doa78p',
                 '0dm9l4rw79',
                 'jowywz7sad',
                 '3p4wzpsnnl',
                 '76c1c77q9d',
                 'w9bqchwv8u',
                 '40yosz2gtw',
                 'afcw2ruo4o',
                 'if10e1sr8g',
                 'awjk1nulrr',
                 'kurmyxjs6i']


def changeCredentials(apikey, accname, streamingtokens):
    import plotly.tools as tools
    tools.set_credentials_file(username=accname,api_key=apikey,stream_ids=streamingtokens)

changeCredentials('CvrH1saCD1wrq5Ye4II2','billy-billy',stream_tokens)