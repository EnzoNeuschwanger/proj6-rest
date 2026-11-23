import requests
import nose2

URL = 'http://127.0.0.1:5001'
SUCESS = {'status' : 'ok'}
FAIL = {'error': 'failed'}
EMPTY = {'error': 'empty'}

example_data = {
                'miles' : '6.2',
                'km' : '10',
                'location': 'Name of Location',
                'open_t': 'Sun 1/1 0:17',
                'close_t': 'Sun 1/1 1:30' 
}


#Test to make sure garbage data won't mess it up
def test_garbage():
    global FAIL
    garbage = {'asdfdsaf' : 'sadfdsfdsa'}
    assert requests.get('http://127.0.0.1:5001/insert', params=garbage).json() == FAIL

#Tests to make sure empty data works
def test_empty():
    global EMPTY
    assert requests.get('http://127.0.0.1:5001/insert', params={}).json() == EMPTY

#This test is dependent on the database being empty and also the previous (one below because nose goes bottom to top) test running
def test_fetch():
    global example_data
    requests.get('http://127.0.0.1:5001/insert', params=example_data)
    r = requests.get('http://127.0.0.1:5001/fetch').json()
    assert r['0'] == example_data
    assert r['1'] == example_data

#Testing correct input. This should work
def test_normal():
    global SUCESS, example_datai
    assert requests.get('http://127.0.0.1:5001/insert', params=example_data).json() == SUCESS


#Fetch should return an empty json file
def test_fetch_empty():
    r = requests.get('http://127.0.0.1:5001/fetch').json()
    assert r == {}

test_garbage()
test_empty()
test_fetch_empty()
test_normal()
test_fetch()

#test = requests.get('http://127.0.0.1:5001/fetch')
#print(test.json())



