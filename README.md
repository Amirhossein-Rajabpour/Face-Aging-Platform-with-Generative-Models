# Face Aging Platfrom with Generative Models
This project focuses on the task of face aging using two generative models: [`Glow`](https://openai.com/research/glow) and [`CycleGAN`](https://junyanz.github.io/CycleGAN/). The main objective was to explore the capabilities of these models in generating realistic and age-progressed images. Furthermore, I used the [`DEX`](https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/) model for estimating the age of the outputs of each model for better qualitative analysis.

The project is implemented using a `microservice` architecture, due to the vast number of conflicting dependencies between these AI models. Each generative model is deployed as a separate microservice, allowing for independent scaling and easy integration with other services. 

## Run the project
You can easily run the whole project without worrying about the dependencies and conflicts just by running the Docker-compose located in the root directory. Everything is handled in the related Dockerfiles.
```
docker-compose up  
```
You should download the pre-trained models and put them in the correct directories. 
* For `Glow`: run [this script](https://github.com/openai/glow/blob/master/demo/script.sh) and place all the files in the `./glow_demo` directory.
* For `CycleGAN`: download the pre-trained models from [here](https://github.com/jiechen2358/FaceAging-by-cycleGAN/tree/master/trained_model) and put them in the `./cyclegan_demo/FaceAging-by-cycleGAN/trained_model` directory
* For `DEX`: download the pre-trained model from [this link](https://github.com/yu4u/age-gender-estimation/releases/download/v0.5/weights.29-3.76_utk.hdf5) and put it in the `./age_estimation/age-gender-estimation-master/age-gender-estimation-master/pretrained_model` directory

## References
* Glow: Better reversible generative models ([link](https://openai.com/research/glow))
* CycleGAN ([link](https://openai.com/research/glow](https://junyanz.github.io/CycleGAN/)))
* DEX: Deep EXpectation of apparent age from a single image ([link](https://openai.com/research/glow](https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/)https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/))
