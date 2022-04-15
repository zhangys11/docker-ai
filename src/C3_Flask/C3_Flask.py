from flask import Flask, render_template, request
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from keras.applications.vgg19 import preprocess_input, decode_predictions
import tensorflow as tf
import keras

app = Flask(__name__)

labels = {0 : 'Normal', 1 : 'Stage1-2', 2: 'Stage3-4'}

config = tf.ConfigProto(
    device_count={'GPU': 0}, # GPU: 0 to use CPU, otherwise, GPU: 1
    intra_op_parallelism_threads=1,
    allow_soft_placement=True
)

config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.7

session = tf.Session(config=config)
keras.backend.set_session(session)

# Use three models
models = []
MODEL_NAME = 'fundus_C3_custom_vgg19_model_2021Oct_fold'

'''
About '_make_predict_function()'

Using theano or tensorflow is a two step process: build and compile the function on the GPU, then run it as necessary. make predict function performs that first step.

Keras builds the GPU function the first time you call predict(). That way, if you never call predict, you save some time and resources. However, the first time you call predict is slightly slower than every other time.

This isn't safe if you're calling predict from several threads, so you need to build the function ahead of time. That line gets everything ready to run on the GPU ahead of time.
'''

for i in range(1,4):
    custom_vgg_model = load_model(MODEL_NAME + str(i) + '.h5')
    custom_vgg_model._make_predict_function() 
    models.append(custom_vgg_model)
    
names = ['Normal', 'Stage1~2', 'Stage3~4']

def predict_label(img_path):

    try:
        with session.as_default():
            with session.graph.as_default():
                W = 224
                thresh = 0.37

                img = image.load_img(img_path, target_size=(W, W))
                x = image.img_to_array(img)
                x = np.expand_dims(x, axis=0)
                x = preprocess_input(x)

                ps = []
                for model in models:
                    p = model.predict(x)
                    ps.append(p)

                prob = np.array(ps).mean(axis = 0)[0]

                title = 'Prediction: {}.  Probability (Normal, Stage1~2, Stage3~4): {}%, {}%, {}%'.format(['Normal','Disease'][int(prob[0] < thresh)], np.round(prob[0]*100), np.round(prob[1]*100), np.round(prob[2]*100))

                return title
    except Exception as ex:
        return 'Prediction Error' + ex #log.log('Prediction Error', ex, ex.__traceback__.tb_lineno)


# routes
@app.route("/", methods=['GET', 'POST'])
def kuch_bhi():
	return render_template("home.html")

@app.route("/about")
def about_page():
	return "Dr. Zhang (oo@zju.edu.cn)"


@app.route("/submit", methods = ['GET', 'POST'])
def get_hours():
	if request.method == 'POST':
		img = request.files['my_image']

		img_path = "static/" + img.filename	
		img.save(img_path)

		p = predict_label(img_path)


	return render_template("home.html", prediction = p, img_path = img_path)


'''
The Flask dev server is not designed to be particularly secure, stable, or efficient. 

By default it runs on localhost (127.0.0.1), change it to app.run(host="0.0.0.0") to run on all your machine's IP addresses.

0.0.0.0 is a special value that you can't use in the browser directly, you'll need to navigate to the actual IP address of the machine on the network. You may also need to adjust your firewall to allow external access to the port.

The Flask quickstart docs explain this in the "Externally Visible Server" section:

    If you run the server you will notice that the server is only accessible from your own computer, not from any other in the network. This is the default because in debugging mode a user of the application can execute arbitrary Python code on your computer.

    If you have the debugger disabled or trust the users on your network, you can make the server publicly available simply by adding --host=0.0.0.0 to the command line.
'''
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new('http://localhost:5003/')
      
if __name__ =='__main__':
    Timer(1, open_browser).start();	
	# use netstat -ano|findstr 5003 to check port use
    app.run(host="0.0.0.0", port=5003) # debug == True
    