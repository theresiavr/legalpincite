python script/retrieval.py -s dev -q par -d par &
python script/retrieval.py -s dev -q par -d case &
python script/retrieval.py -s dev -q case -d case &
wait

python script/retrieval.py -s test -q par -d par &
python script/retrieval.py -s test -q par -d case &
python script/retrieval.py -s test -q case -d case &
wait