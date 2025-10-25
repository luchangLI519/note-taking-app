---
title: Lab 2 
author: Liluchang
student_id: 25119475g
date: 2025-10-25
---

# GOAL

 • Implement GenAI features in the notes taking app (Translation and Notes generation)
 
 • Refactor the app to use Postgres in Supabase (Cloud database)
 
 • Refactor the app and deploy the app in Vercel

---

## 1. Use Copilot to complete the environment dependencies of the cloned project

<img width="960" height="436" alt="51253a72a30ac19c35464485dc19c7bd" src="https://github.com/user-attachments/assets/3c1188fd-4acc-4eb8-b560-3a95ff055f73" />


## 2. Change the color of the website and buttons


> ![pip-success](./images/pip-success.p<img width="1402" height="1340" alt="94eda0833dbb46218a72935815266867" src="https://github.com/user-attachments/assets/d0094591-f90f-49cd-a239-d3b82bbfc313" />
ng)

After the color of this website changed, new notes would overwrite old notes, so I asked Colipot to help me modify the code.

> <img width="1418" height="1030" alt="95b16af42b6a0d4521cf7995449ef808" src="https://github.com/user-attachments/assets/d28839aa-6e86-410f-bf2a-0b18d27adb38" />

The modified website can run normally.


## 3. Add some options to choose from, such as tagging notes and recording the time.


<img width="2880" height="1800" alt="287a807b3d0d4d285a26b0d4a86faa0a" src="https://github.com/user-attachments/assets/5241773b-cd35-442d-9084-acd319dbb800" />


## 4. Added the ability to sort the note lists on the left side of the page by dragging and dropping


<img width="2880" height="1704" alt="80afd35d1f569e229d5bdafa52358fec" src="https://github.com/user-attachments/assets/0dca1bc5-9cc2-4b90-88a1-b52ebdfe7ad1" />

<img width="2880" height="1800" alt="816d6b48ffb54cfaf22a9b0caa22379c" src="https://github.com/user-attachments/assets/51d00b38-9d16-4a34-956b-a77e9c4d6b18" />

I encountered the same problem here as before: after adding new features, the code always loses the previous note data, so I created a few more data entries.


## 5.Add GenAI’s translation function


This is based on the content taught by the teacher in class. First, I created the llm.py file, and then implemented the translation code in that file. After setting the API in Git, I used it in the file to allow AI to perform translation through the llm file.

<img width="2880" height="1704" alt="77497f25145d2496653dd6c95e0ae819" src="https://github.com/user-attachments/assets/0cb8a9cc-8972-400c-9708-07ba36306e2e" />


## 6.Supabase deployment


Create ProjectCreate a new project in the Supabase console and set the database password. Wait for the resources to be ready, initialize the database, and copy the connection string. Integrate it into your application and write it into environment variables for the application to connect at runtime. Next, perform migrations and generate schemas. Go back to Database → Tables to confirm that the tables have been created and can be queried. Finally, configure DATABASE_URL and DIRECT_URL in the server environment variables and start the application.

<img width="1980" height="956" alt="aa354839702be4897beb1bf5769d7968" src="https://github.com/user-attachments/assets/794757d4-d7c2-4993-b1cc-2c5920cd26ca" />

<img width="1193" height="783" alt="bc05a385b031433829d39396b3232e2d" src="https://github.com/user-attachments/assets/d9c7af59-92fd-4910-96e9-51974e7109b3" />

<img width="1202" height="844" alt="71ae4342c9080edc40aee91b924a348b" src="https://github.com/user-attachments/assets/f78ef060-c9dd-4013-bf40-f1afbcefc5ce" />

<img width="1881" height="504" alt="24210a80be91379f4e88a617ecf146fa" src="https://github.com/user-attachments/assets/6a4cc575-62b0-4eba-97af-674ecb97598f" />


## 7.vercel deployment

Host the code on Git, then import and create a project via Dashboard → New Project → select the Git repository and branch → Continue. Set the Team, Project Name, Root Directory=./, then proceed to choose the framework and build settings, followed by adding environment variables. Finally, you can perform a one-click deployment to get a preview URL, and merging into the main branch will automatically publish it to production.

<img width="968" height="542" alt="cedd095981270853c533575644211be2" src="https://github.com/user-attachments/assets/6102a6df-b6ac-4c3d-afaa-7638588e75eb" />

<img width="1802" height="540" alt="0ab7e67b6b2ccbbe798524e2d51659b8" src="https://github.com/user-attachments/assets/2fac976f-dd5f-4808-a759-9f6ee877c8b8" />

<img width="599" height="909" alt="c92d9b00f88b2c614473b2f069b69c43" src="https://github.com/user-attachments/assets/3df26c7a-8db2-4d19-ae2a-38da6b2a44f4" />

<img width="700" height="387" alt="a5af2cfcdc492de5dd691ee2af0caf95" src="https://github.com/user-attachments/assets/195efddb-c24d-4706-8b28-75491b05fad4" />

<img width="689" height="731" alt="58848fc9dd039c162fa18ae490fca1d5" src="https://github.com/user-attachments/assets/77563bbc-107a-4ee6-9429-a423e4abd063" />


## 8.Function demonstration

![4fae9aebfeff0f92f05c3dd58cbc7b69](https://github.com/user-attachments/assets/4fc63470-11d6-4c88-8ed1-f1203a9da716)

![fcaff8efaffb94ef1d5d529024ca71af](https://github.com/user-attachments/assets/8182764b-4bbf-4d56-9acb-faccd7d47d9f)


![2c92e1a2064b4154c54d21c2c08d0207](https://github.com/user-attachments/assets/a9c943a0-9402-4dbc-b015-2f8e2a387a5a)


![2a619de32ca99fd62da3d624a5a5fe26](https://github.com/user-attachments/assets/d1e2aadf-a9fd-494c-bca6-80b20d3948b5)


![d26a938711f813822a4a2cf38f269f8a](https://github.com/user-attachments/assets/8fad41f1-a605-49f2-9734-dca307e7a112)


## 9.Problems and Solutions


1.When creating a new feature, adding new notes will overwrite the old notes.

solution：It was a database issue; once the database was debugged, everything was fine.

<img width="1584" height="638" alt="3268eb8f69a2ec0029bb6649d3bbbd85" src="https://github.com/user-attachments/assets/14d42614-becf-41f3-90f5-4a60f25fba88" />

<img width="1210" height="960" alt="0b4093175a5adcaeb557ee05fc76dce1" src="https://github.com/user-attachments/assets/7c7f5669-2c3b-423e-94ba-cb177be15013" />


2.Syntax/parse errors that occur when trying to use a one-liner Python command in PowerShell (representing quote/escape issues):SyntaxError: unterminated string literal (detected at line 1)SyntaxError: invalid syntaxCommandNotFoundException (forgot to take a screenshot of this error)

solution：The error is mainly caused by executing complex one-liner Python commands directly in PowerShell, where the shell's quote/backslash escaping leads to syntax errors or command parsing failures. It's not a problem with Python itself, but rather that the command-line string gets corrupted.

<img width="2880" height="1800" alt="d34b62cec76abd840e86836eced0298a" src="https://github.com/user-attachments/assets/b92f5660-7541-43f4-940a-371c6ec58766" />


3.Network connection issues, database deployment unsuccessful, and the translation function cannot be used properly.The timeout issue keeps occurring.

solution：After checking IPv4 and IPv6, it was found that there was a network issue on the computer. After switching to another computer, the project could be deployed normally.

<img width="2880" height="1704" alt="80afd35d1f569e229d5bdafa52358fec" src="https://github.com/user-attachments/assets/31be1e80-96f0-4e2a-9de6-f5da03c6bf50" />

![2b90e5ce6c2c3c8b2b8f3f01b4c650ea](https://github.com/user-attachments/assets/9cb98968-36be-4bc1-bdb5-78d89eb6beac)
