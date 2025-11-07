# CS3103-Assignment4-Group11

Adaptive Hybrid Transport Protocol for Games

Test with:

1. Open one terminal and type: python receiver_app.py --duration 6
2. On another terminal, immediately type: python sender_app.py --duration 5

Alternatively:
1. Run `python runner.py` (default duration is 5 seconds, and default packet rate is 20 packets per second)
2. You can customize the duration and packet rate using the `--duration` and `--rate` arguments respectively.


### Finding Value of Optimal Skip Threshold
Extensive tests to find optimal value of skip threshold t and to retrieve performance metrics under different network
conditions and different skip thresholds t are done using a modified version in branch `metric-testing` where the code
is modified to allow skip threshold t to put input as a command line argument with flag `--threshold`.

> Details on how to find value of optimal skip threshold through testing is in `README.md` of branch `metric-testing`