# 1. Project Overview
The T4 project was a state-of-the-art markerless pose estimation software used to evaluate gait - running and walking movement - in Physical Therapy (PT) patients. It was designed to address a set of problems encountered in physical therapy gait analysis:
    
1. Lack of quantitative assessment tools
2. Large time demand for PT's to manually review videos of patient gait patterns
3. Improve standardization and accuracy of gait evaluation processes

We sought to address these issues by collecting video data of patient gait patterns in a specially designed room, then using purpose-made computer vision and machine learning models to measure the movement of the patients in those videos. 

# 2. Solution Architecture
## 2.1. A Note on Data Security
This project involved collecting data on patients in a clinical environment. So, we had to ensure patient safety and data integrity by adhering to HIPAA Protected Health Information regulatory guidance. Therefore, data was handeled entirely within the clinical environment, and utilized encypted servers on premises and the cloud storage infrastructure (OneDrive) that was the property of the clinics that we worked with.

#### Figure 1: Data Flow Overview
![alt text](readme_assets/DataFlowOverview.png)
#### Figure 2: Photos of Process
![alt text](readme_assets/TechDescriptionCombinedGraphic.png)
## 2.2. Data Collection
Video data was gathered from 4 directions, as can be seen in Figure 2, Section A and B. Collection occured at specific speeds and for 10 seconds blocks. Sony cameras were used for three reasons. First, they could be mounted in a fixed position to the front, sides, and behind the patient. Second, they could record in a synced state, with the same frame number being maintained through all four cameras. Third, they had high frame rate capabilities, allowing for more data capture.

This culminated in a purpose built room with a modified treadmill (physically altered to reduce sagittal occlusion), the cameras that were previously mentioned, and a computer interface used by clinicians to record data. Before training the models used to identify joints and gait patterns, the T4 team and clinicians had to **gather more than 400 video recordings of patients. The original dataset was composed of these samples** and enabled the decvelopment mentioned later.

A semi-automated process was devised to enable quick and easy data collection during dataset development and after going live. The videos of a patients gait were recorded and uploaded in to a patient's folder. A Powershell script on the local encrypted server would watch for these events (dev/bin/WatchToFlip.ps1). The videos would be **pre-processed by flipping the videos to the correct orientation, renaming them, and increasing contrast of the video.** 

## 2.3. Data Processing
These videos were then put in to a processing directory where the product/stride/main.py script would be run. This script would **use our pose estimation models to infer the position of joints**, seen in Figure 2 Section B. This pixel data was stored in .h5 files. Basic trigonometry was used to calculate the angles between dots along specified axis (product/stride/angle_finder.py). After this process was completed, **a .csv file containing all of the calculated angles was created, as well as a video with the joints and angles written on it.** 

Finally, at the end of video and .csv creation, a machine learning model would be run on the .csv. It would take a row of angles, and predict the "stance" or phase of gait that the individual was in during that row, see Figure 2 Section C. This was an entireley **novel development, to our knowledge, and a specific request from the PT's**. Having the phase of gait labeled on the .csv and frame simplified the review process. 

#### Figure 3: Data Review and Reporting
![alt text](readme_assets\VideoandT4ReportPhoto.png)

## 2.4. Data Processing and Sharing
The .csv file could then be reviewed by the PT. The doctor would upload the .csv to our deployed Dash App. We used this to allow PT's to access our data analysis features and conduct individualized reviews of the data with each patient. They could **highlight the phase of gait, isolate the perspective of the movement plane (ex. Anterior Frontal), and look at the movement patterns for each joint**. These reports also allowed the PT to input patient information and perscriptive exercise plans for the patient and email it to them from the PT's email address. 

## 2.5. Data Storage
All raw and generated data was then archived in patient folders on the local encrypted server used for storage and in the HIPAA compliant cloud service used by these clinics. This process was automated, and managed by cloud tools and Powershell scripts installed on ther server that continuously monitored relevant directories.

# 3. Technical Development
## 3.1. Joint Identification with Neural Networks
The Physical Therapists that conduct gait analysis go through extensive training to review patient movement patterns (usually directly watching them, but also with videos) and identify altered movement patterns. This process relies heavily on the relative relationship of the patients joints. Therefore, the first step of our process was to learn the *exact* location that the PT's were looking at, right down to the specific bone potrusions. These sights were different for the anterior, sagittal, and posterior planes, so we decided to create three seperate models to identify the necessary joints for diagnoses from these perspectives. We then documented this for our labeling team.

Next, we reviewed the literature and found a paper from [Alexander Mathis, et al.](https://www.nature.com/articles/s41593-018-0209-y). In this paper the team describes a process of labeling the "body parts" of animals in videos. Then, they fit a pre-trained Residual Neural Network (ResNet-50) to the data, a process called transfer learning. This process is documented in the GitHub repository [DEEPLABCUT](https://github.com/DeepLabCut/DeepLabCut).

We utilized the labeling and training tools provided by the DEEPLABCUT package to label a proprietary dataset that we curated. This dataset contained video data of more than 400 patients. We took care to ensure that the dataset was representative of the diversity (size, shape, skin color, etc.) of the population so that the models created from it would perform on every patient. We did this by estimating the normal distribution of our patient population for relevant variables, and sought to label patients on the outer edges of this distribution. In practice, this process proved successful.

Labeling was completed by a team of Biomedical Engineers, with guidance and reviews from the PT's. Additionally, as models were run with patient data, low performers were identified, and used to add to the dataset that we curated. This created a feedback loop that allowed us to improve the models over time and with real-world data. 

**The approach of using a specialized dataset and fine-tuning a ResNet-50 model allowed these models to outperform other markerless and marker-based pose estimation software, which proved to be brittle when encountering occlusion, poorly handeled gait movement, and/or patients that were on the edge of normal distribution for some variables.**

## 3.2. Phase of Gait Recognition Models
Interviews with the Physical Therapists revealed that they were conducting manual frame-by-frame reviews of video data to identify specific phases of gait and review the patients posture in these phases. This was a key feature that we used to reduce the time dedicated to collecting quantitative data about the patient.

Before going further, here is a brief explanation of the pahses of gait:
The human gait cycle can be seperatered into specific sections that **must occur** in order for the gait cycle to be complete. The gait cycle is seperated into swing (when the foot is off the ground) and stance (foot is touching the ground). 
Here are the sub-phases for the stance phase:
- Initial Strike: The first frame in which the foot is making contact with the ground following the swing phase
- Loading Response: The phase in between Initial Strike and Midstance.
- Midstance: The point of maximum triple flexion. Typically, when the midpoint of the foot is nearly in alignment with the hip “keypoint.”
- Terminal Stance: The propulsion phase in between Midstance and Terminal Stance.
- Toe Off: The last frame with the toe (and/or foot) still on the ground.

#### Figure 4: Phase of Gait Labeling Process
![alt text](readme_assets/FrameLabelingProcess.png)
With these definitions, the labeling team went frame by frame and labeled a dataset for the phases of gait. The input data, in this case, was the angle information that was calculated by the joint identification models. These labels were randomly sampled and reviewed by a team of PT's to ensure that the standards were upheld. A total of 4000 labeled rows were generated by the team.

Do to the nature of phase labeling, this dataset was inherently inbalanced. Some phases represent transition states between instantaneous states. For example, the 'Initial Strike' phase was contained in one frame, while the 'Loading Phase' was usually spread between 10-15 frames. To address this, we used the data augmentation strategy Synthetic Minority Over-sampling Technique (SMOTE) to create synthetic examples of under represented phases, and we undersampled the phases that were more represented. Intuitively, one might expect this to create a model which is inaccurate on real-world data, but further experimentation showed that models trained on SMOTE datasets outperformed the inbalanced datasets. These dataset creation processes can be reviewed in dev/pgr_ml/dataset_creator.py and systematic_test.py.

A systematic testing suite was created to compare the performance of models trained with different machine learning algorithms. We compared 6 different models that were expected to perform well on this dataset. Linear (Multi-Class Log Regression), Non-linear (Decision Tree, SVM, K-Nearest Neighbor), and Ensemble (Random Trees, Extra Trees) were used. This approach was used to experimentally explore what algorithm would perform best on this dataset. A k-fold cross validation test was used to provide a reliable estimate of model accuracy and reduce the risk of overfitting in a single train-test split. The results can be seen below in Figure 5. 

#### Figure 5: Boxplot of Accuracy and Standard Deviation of the K-fold Cross Validation Test
![alt text](readme_assets\BoxplotOfModels.png)

Further hyperparameter tuning and increased size of the dataset created a model that was **98% accurate** when trained with the Extra Trees algorithm. This approach can be reviewed in the dev/pgr_ml/prototyper.ipynb file. 

## 3.4. Data Analysis Feature
The details of how this data is generated have been covered above. The purpose of this section is to connect the output of the technical development to the original business problems encountered by the PT's.

### 3.4.1. Angles

### Phases of Gait

## 3.5. App Deployment
During the production phase of the T4 Movement project, a [Dash App](https://dash.plotly.com/) was hosted on a Heroku server. The app allowed PT's from multiple clinics to simulateously access the dashboard, securely upload the .csv file that contained gait data (angles and phases of gait for all 4 planes; Note: No PHI was stored in these files.), and conduct an in-depth review of the data using the analytical tools mentioned earlier. 

# Results and Impact
*Explain the results achieved, including any measurable improvements in accuracy, efficiency, or feedback from users.*

# Technologies Used
*List the key technologies, programming languages, libraries, and frameworks that were used in the project.*

# Lessons Learned
*Reflect on what you learned from this project, both technically and in terms of working on a long-term software project.*
