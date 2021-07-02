# Alexa Transcript Downloader

This is an automatic script that asynchronously downloads all historic transcript data of specified Amazon Alexa Accounts (https://alexa.amazon.de/). 



## Prerequisites 

- Internet Access
- Installed Git 
- Installed Python 3 and dependencies of the script 
- Installed Chrome 

## Installation



## Execution

You execute the script by first opening the command line. Press WINDOWS + R, then enter "cmd" and press Enter. 

You now have to navigate into the folder of the script. Type "cd " and then drag and drop the folder of the script into the command line. The command line will now look something like this: 

```
cd C:\Users\Test\Documents\script
```

Now press enter. 

If you type in "dir" into the command line and press enter, something like this should appear: 

```
02.07.2021  13:50             4.722 .gitignore
02.07.2021  14:06    <DIR>          .idea
28.04.2021  13:09        11.310.592 chromedriver.exe
02.07.2021  14:08                49 credentials.yml
17.06.2021  15:23             5.650 dtos.py
02.07.2021  13:24             5.575 in_out.py
02.07.2021  13:47             4.668 main.py
```

If you see "main.py" in the console output. You are set the execute the script. 

You execute the script by typing in: 

```
python3 main.py credentials.yml
```

The script the starts executing and Chrome should open several times to login to the accounts. Each first login to an account must be confirmed by clicking on a link in the confirmation email. One option is to login to each account manually before executing the script. You can also click on the link in the confirmation email while the script is running. It then waits until you clicked the link and then continues. 



## Input

There is a file "credentials.yml". It contains all the credentials for all accounts. 

The content looks like this: 

```
test@web.de: password

test2@web.de: password2
```

Each line in the file corresponds to the credentials of the username and password of an account. Username and password are separated by a colon. 

## Output

The script generates a folder each time it is executed. 

The name of the folder looks like this:  "2021_07_02 14_00_34". This means the script was executed on 2nd of July 2021 at 14:00:34. 

Inside this folder, the script generates subfolders for each account that is specified in "credentials.yml". Each subfolder is named by the email of the account and contains all the transcript data of the account. 

There is also a file called "all_records.xlsx" that contains the sum of all records of all accouts.

The content of the excel files looks like this: 

|      | record_key                                                | recordType    | timestamp           | customerId    | device_name | device_entity_id | is_binary_feedback_provided | is_feedback_positive | utteranceType | domain   | intent              | skillName                                                   | voice1Key           | voice1Type                                                   | voice1UtteranceId   | voice1Timestamp                | voice1Transcript                                            | voice1AgentVisualName | voice2Key                                                    | voice2Type          | voice2UtteranceId | voice2Timestamp | voice2Transcript | voice2AgentVisualName | voice3Key | voice3Type | voice3UtteranceId | voice3Timestamp | voice3Transcript | voice3AgentVisualName |
| ---- | --------------------------------------------------------- | ------------- | ------------------- | ------------- | ----------- | ---------------- | --------------------------- | -------------------- | ------------- | -------- | ------------------- | ----------------------------------------------------------- | ------------------- | ------------------------------------------------------------ | ------------------- | ------------------------------ | ----------------------------------------------------------- | --------------------- | ------------------------------------------------------------ | ------------------- | ----------------- | --------------- | ---------------- | --------------------- | --------- | ---------- | ----------------- | --------------- | ---------------- | --------------------- |
| 0    | A7UOF28QO3UXO#1625037867407#AWZZ5CVHX2CD#G000RA1102560JBR | VOICE_HISTORY | 2021-06-30 07:24:27 | A7UOF28QO3UXO | Testdevice  |                  | FALSCH                      | FALSCH               | GENERAL       | Echo.SDK | PersonalityQAIntent | 1625037867407#AWZZ5CVHX2CD#G000RA1102560JBR#1625037865869-0 | CUSTOMER_TRANSCRIPT | AWZZ5CVHX2CD:1.0/2021/06/30/07/G000RA1102560JBR/24:25::TNIH_2V.1d76b4e9-39d4-4d7e-811b-df7a0f2807f0LPM/0 | 2021-06-30 07:24:25 | alexa das wünsche ich dir auch | 1625037867407#AWZZ5CVHX2CD#G000RA1102560JBR#1625037867409-2 | ALEXA_RESPONSE        | AWZZ5CVHX2CD:1.0/2021/06/30/07/G000RA1102560JBR/24:25::TNIH_2V.1d76b4e9-39d4-4d7e-811b-df7a0f2807f0LPM/0 | 2021-06-30 07:24:27 | Danke!            |                 |                  |                       |           |            |                   |                 |                  |                       |

