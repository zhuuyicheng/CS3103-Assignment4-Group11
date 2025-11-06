#!/bin/bash

# Clear logs

rm log.log 
rm output.out

# Emulate network condition on the lo interface

# Low loss conditions

sudo tc qdisc del dev lo root
sudo tc qdisc add dev lo root netem delay 100ms 10ms loss 1%

echo 'delay 100ms, jitter 10ms, loss 1%'
echo 'rate 20'

python3 runner.py --duration 30 --threshold 0.01 --sender-port 10000 --receiver-port 10001 >> output.out &
python3 runner.py --duration 30 --threshold 0.05 --sender-port 10002 --receiver-port 10003 >> output.out &
python3 runner.py --duration 30 --threshold 0.1 --sender-port 10004 --receiver-port 10005 >> output.out &
python3 runner.py --duration 30 --threshold 0.2 --sender-port 10006 --receiver-port 10007 >> output.out &
python3 runner.py --duration 30 --threshold 0.3 --sender-port 10008 --receiver-port 10009 >> output.out &
python3 runner.py --duration 30 --threshold 0.4 --sender-port 10010 --receiver-port 10011 >> output.out &
python3 runner.py --duration 30 --threshold 0.5 --sender-port 10012 --receiver-port 10013 >> output.out &
python3 runner.py --duration 60 --threshold 0.01 --sender-port 10014 --receiver-port 10015 >> output.out &
python3 runner.py --duration 60 --threshold 0.05 --sender-port 10016 --receiver-port 10017 >> output.out &
python3 runner.py --duration 60 --threshold 0.1 --sender-port 10018 --receiver-port 10019 >> output.out &
python3 runner.py --duration 60 --threshold 0.2 --sender-port 10020 --receiver-port 10021 >> output.out &
python3 runner.py --duration 60 --threshold 0.3 --sender-port 10022 --receiver-port 10023 >> output.out &
python3 runner.py --duration 60 --threshold 0.4 --sender-port 10024 --receiver-port 10025 >> output.out &
python3 runner.py --duration 60 --threshold 0.5 --sender-port 10026 --receiver-port 10027 >> output.out &

wait
echo 'rate 80'

python3 runner.py --duration 30 --threshold 0.01 --rate 80 --sender-port 10000 --receiver-port 10001 >> output.out &
python3 runner.py --duration 30 --threshold 0.05 --rate 80 --sender-port 10002 --receiver-port 10003 >> output.out &
python3 runner.py --duration 30 --threshold 0.1 --rate 80 --sender-port 10004 --receiver-port 10005 >> output.out &
python3 runner.py --duration 30 --threshold 0.2 --rate 80 --sender-port 10006 --receiver-port 10007 >> output.out &
python3 runner.py --duration 30 --threshold 0.3 --rate 80 --sender-port 10008 --receiver-port 10009 >> output.out &
python3 runner.py --duration 30 --threshold 0.4 --rate 80 --sender-port 10010 --receiver-port 10011 >> output.out &
python3 runner.py --duration 30 --threshold 0.5 --rate 80 --sender-port 10012 --receiver-port 10013 >> output.out &
python3 runner.py --duration 60 --threshold 0.01 --rate 80 --sender-port 10014 --receiver-port 10015 >> output.out &
python3 runner.py --duration 60 --threshold 0.05 --rate 80 --sender-port 10016 --receiver-port 10017 >> output.out &
python3 runner.py --duration 60 --threshold 0.1 --rate 80 --sender-port 10018 --receiver-port 10019 >> output.out &
python3 runner.py --duration 60 --threshold 0.2 --rate 80 --sender-port 10020 --receiver-port 10021 >> output.out &
python3 runner.py --duration 60 --threshold 0.3 --rate 80 --sender-port 10022 --receiver-port 10023 >> output.out &
python3 runner.py --duration 60 --threshold 0.4 --rate 80 --sender-port 10024 --receiver-port 10025 >> output.out &
python3 runner.py --duration 60 --threshold 0.5 --rate 80 --sender-port 10026 --receiver-port 10027 >> output.out &

wait

# Average loss conditions

sudo tc qdisc del dev lo root
sudo tc qdisc add dev lo root netem delay 100ms 10ms loss 5% 

echo 'delay 100ms, jitter 10ms, loss 5%'
echo 'rate 20'

python3 runner.py --duration 30 --threshold 0.01 --sender-port 10000 --receiver-port 10001 >> output.out &
python3 runner.py --duration 30 --threshold 0.05 --sender-port 10002 --receiver-port 10003 >> output.out &
python3 runner.py --duration 30 --threshold 0.1 --sender-port 10004 --receiver-port 10005 >> output.out &
python3 runner.py --duration 30 --threshold 0.2 --sender-port 10006 --receiver-port 10007 >> output.out &
python3 runner.py --duration 30 --threshold 0.3 --sender-port 10008 --receiver-port 10009 >> output.out &
python3 runner.py --duration 30 --threshold 0.4 --sender-port 10010 --receiver-port 10011 >> output.out &
python3 runner.py --duration 30 --threshold 0.5 --sender-port 10012 --receiver-port 10013 >> output.out &
python3 runner.py --duration 60 --threshold 0.01 --sender-port 10014 --receiver-port 10015 >> output.out &
python3 runner.py --duration 60 --threshold 0.05 --sender-port 10016 --receiver-port 10017 >> output.out &
python3 runner.py --duration 60 --threshold 0.1 --sender-port 10018 --receiver-port 10019 >> output.out &
python3 runner.py --duration 60 --threshold 0.2 --sender-port 10020 --receiver-port 10021 >> output.out &
python3 runner.py --duration 60 --threshold 0.3 --sender-port 10022 --receiver-port 10023 >> output.out &
python3 runner.py --duration 60 --threshold 0.4 --sender-port 10024 --receiver-port 10025 >> output.out &
python3 runner.py --duration 60 --threshold 0.5 --sender-port 10026 --receiver-port 10027 >> output.out &

wait
echo 'rate 80'

python3 runner.py --duration 30 --threshold 0.01 --rate 80 --sender-port 10000 --receiver-port 10001 >> output.out &
python3 runner.py --duration 30 --threshold 0.05 --rate 80 --sender-port 10002 --receiver-port 10003 >> output.out &
python3 runner.py --duration 30 --threshold 0.1 --rate 80 --sender-port 10004 --receiver-port 10005 >> output.out &
python3 runner.py --duration 30 --threshold 0.2 --rate 80 --sender-port 10006 --receiver-port 10007 >> output.out &
python3 runner.py --duration 30 --threshold 0.3 --rate 80 --sender-port 10008 --receiver-port 10009 >> output.out &
python3 runner.py --duration 30 --threshold 0.4 --rate 80 --sender-port 10010 --receiver-port 10011 >> output.out &
python3 runner.py --duration 30 --threshold 0.5 --rate 80 --sender-port 10012 --receiver-port 10013 >> output.out &
python3 runner.py --duration 60 --threshold 0.01 --rate 80 --sender-port 10014 --receiver-port 10015 >> output.out &
python3 runner.py --duration 60 --threshold 0.05 --rate 80 --sender-port 10016 --receiver-port 10017 >> output.out &
python3 runner.py --duration 60 --threshold 0.1 --rate 80 --sender-port 10018 --receiver-port 10019 >> output.out &
python3 runner.py --duration 60 --threshold 0.2 --rate 80 --sender-port 10020 --receiver-port 10021 >> output.out &
python3 runner.py --duration 60 --threshold 0.3 --rate 80 --sender-port 10022 --receiver-port 10023 >> output.out &
python3 runner.py --duration 60 --threshold 0.4 --rate 80 --sender-port 10024 --receiver-port 10025 >> output.out &
python3 runner.py --duration 60 --threshold 0.5 --rate 80 --sender-port 10026 --receiver-port 10027 >> output.out &

wait

# High loss conditions

sudo tc qdisc del dev lo root
sudo tc qdisc add dev lo root netem delay 100ms 10ms loss 15% 

echo 'delay 100ms, jitter 10ms, loss 15%'
echo 'rate 20'

python3 runner.py --duration 30 --threshold 0.01 --sender-port 10000 --receiver-port 10001 >> output.out &
python3 runner.py --duration 30 --threshold 0.05 --sender-port 10002 --receiver-port 10003 >> output.out &
python3 runner.py --duration 30 --threshold 0.1 --sender-port 10004 --receiver-port 10005 >> output.out &
python3 runner.py --duration 30 --threshold 0.2 --sender-port 10006 --receiver-port 10007 >> output.out &
python3 runner.py --duration 30 --threshold 0.3 --sender-port 10008 --receiver-port 10009 >> output.out &
python3 runner.py --duration 30 --threshold 0.4 --sender-port 10010 --receiver-port 10011 >> output.out &
python3 runner.py --duration 30 --threshold 0.5 --sender-port 10012 --receiver-port 10013 >> output.out &
python3 runner.py --duration 60 --threshold 0.01 --sender-port 10014 --receiver-port 10015 >> output.out &
python3 runner.py --duration 60 --threshold 0.05 --sender-port 10016 --receiver-port 10017 >> output.out &
python3 runner.py --duration 60 --threshold 0.1 --sender-port 10018 --receiver-port 10019 >> output.out &
python3 runner.py --duration 60 --threshold 0.2 --sender-port 10020 --receiver-port 10021 >> output.out &
python3 runner.py --duration 60 --threshold 0.3 --sender-port 10022 --receiver-port 10023 >> output.out &
python3 runner.py --duration 60 --threshold 0.4 --sender-port 10024 --receiver-port 10025 >> output.out &
python3 runner.py --duration 60 --threshold 0.5 --sender-port 10026 --receiver-port 10027 >> output.out &

wait
echo 'rate 80'

python3 runner.py --duration 30 --threshold 0.01 --rate 80 --sender-port 10000 --receiver-port 10001 >> output.out &
python3 runner.py --duration 30 --threshold 0.05 --rate 80 --sender-port 10002 --receiver-port 10003 >> output.out &
python3 runner.py --duration 30 --threshold 0.1 --rate 80 --sender-port 10004 --receiver-port 10005 >> output.out &
python3 runner.py --duration 30 --threshold 0.2 --rate 80 --sender-port 10006 --receiver-port 10007 >> output.out &
python3 runner.py --duration 30 --threshold 0.3 --rate 80 --sender-port 10008 --receiver-port 10009 >> output.out &
python3 runner.py --duration 30 --threshold 0.4 --rate 80 --sender-port 10010 --receiver-port 10011 >> output.out &
python3 runner.py --duration 30 --threshold 0.5 --rate 80 --sender-port 10012 --receiver-port 10013 >> output.out &
python3 runner.py --duration 60 --threshold 0.01 --rate 80 --sender-port 10014 --receiver-port 10015 >> output.out &
python3 runner.py --duration 60 --threshold 0.05 --rate 80 --sender-port 10016 --receiver-port 10017 >> output.out &
python3 runner.py --duration 60 --threshold 0.1 --rate 80 --sender-port 10018 --receiver-port 10019 >> output.out &
python3 runner.py --duration 60 --threshold 0.2 --rate 80 --sender-port 10020 --receiver-port 10021 >> output.out &
python3 runner.py --duration 60 --threshold 0.3 --rate 80 --sender-port 10022 --receiver-port 10023 >> output.out &
python3 runner.py --duration 60 --threshold 0.4 --rate 80 --sender-port 10024 --receiver-port 10025 >> output.out &
python3 runner.py --duration 60 --threshold 0.5 --rate 80 --sender-port 10026 --receiver-port 10027 >> output.out &

wait

sudo tc qdisc del dev lo root
