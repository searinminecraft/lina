# linaSTK Privacy Policy

*Yes, I had to make a privacy policy, for those concerned*

Thanks for taking the time at reading the privacy policy for the linaSTK bot. We take your privacy very seriously and we will never sell your data to a third party, or use it to serve ads to you.

This privacy policy applies to the official instance of linaSTK (both production and development versions). Other instances of the bot may adopt this privacy policy if they wish.

## Information the bot collects

### STK Seen and Player Tracking
We collect the required data in order for it to work:

* Username
* User Country (if applicable)
* Server Name
* Server Country

We store this data to a PostgreSQL database in order to retrieve and store player activity data (which makes player tracking and `stk-seen` to work). We will not use this data for any malicious intent, unless you were to for example, stalk a person.

## How we get all of the information
Without getting too technical here, we use the official SuperTuxKart APIs to be able to get the information such as user information and online servers and their information. They are not collected and stored, except for some parts of server information for player tracking and `stk-seen`

## Logging
We log activity of our bot (including HTTP requests and errors) in the server's console for diagnostic purposes, and it may contain sensitive data including an STK Server's IP address.

We know that there may be servers that are created using the "Create Server" option in SuperTuxKart and can show an individual's IP Address, but there is no way we can determine that the server is created using that feature. Rest assured, we **DO NOT** store the log output to a text file. You can look through the source code if you want to prove me wrong.

## Other
The server's IP Address is shown in the `online` command, which may raise concerns about individuals' IP Addresses being shown (See [Logging](#logging) for more information). We might implement an option in the config to disable showing IP addresses in the `online` command or remove it entirely.

## Your rights
If you believe that linaSTK raises concerns about your privacy and data rights, you want to request data associated with you be deleted, or have any questions or other concerns, you may contact me using one of the communication methods below.

## Contact
Discord: searinminecraft
Revolt (preferred, but please use the `#Off-Topic Unbridged` channel): https://rvlt.gg/1Rw7Nevx
Email: linamoonlight@transgender.army


###### Last updated: 2023-08-31
