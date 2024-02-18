#Gradescope.py
This program is a revised compilation of scripts originally created by Arindaam Roy. It creates a directory with files of all student submissions, checks for potential plagiarism, checks code for illegal imports, and uploads submissions to Gradescope. 

#Discord Bot (bot.py) Documentation
**Overview**
The bot is designed to facilitate interaction between students and tutors in a learning community hosted on a Discord server. The bot manages channels for asking questions, answering them, and registering for tutoring sessions. It ensures the proper flow of interaction, keeping the server organized and efficient.

**Initialization**
The bot is initialized with a token, which is not provided in the code for security reasons.

bot = interactions.Client(token='<token>')
The waiting_list is a global list that will hold the queue of students waiting for a tutor.

global waiting_list
waiting_list = []
Two button objects are defined for user interaction: public_button and private_button.

**Utility Functions**
There are several utility functions that help in retrieving information about categories and roles in the Discord server:

get_categories(ctx): This function returns the IDs of the channels "ASK HERE", "ACTIVE QUESTIONS", "TUTORING", and "ANSWERED QUESTIONS".

tutor_check(ctx): This function checks if a user has the role of "Tutor" and returns a boolean value.

get_relevant_roles(ctx): This function returns the IDs of the roles "Tutor", "@everyone", "Student", and "Active Tutor".

**Commands**
Commands in the bot are defined using the @bot.command decorator. Here are the commands defined in the bot:

resolve: This command is used to close a channel. It checks if the channel is open and if the user executing the command has the necessary permissions. If the channel is private, it deletes the message history.

register: This command allows a user to get in line for a tutor. It adds the user to the waiting_list and notifies them of their position.

next: This command allows a tutor to notify the next student in line that they are ready. It checks if the user executing the command is a tutor and if there is a student in line.

signin: This command allows a tutor to sign into their tutoring shift. It checks if the user executing the command is a tutor and if they are not already signed in.

signout: This command allows a tutor to sign out of their tutoring shift. It checks if the user executing the command is a tutor and if they are not already signed out.

forceresolve: This is a debug command reserved for use by admins to force any channel to become a new Ask Here channel. If a channel ever fails to resolve into a proper state, an admin can use this command to fix it.

**Button Responses**
There are two button responses defined in the bot, public_button_response and private_button_response. These responses are triggered when a user clicks on the respective button. They handle the process of opening a question in a public or private channel.

**Running the Bot**
The bot is started with the bot.start() command at the end of the script.

Note
Please remember to replace <token> with the actual bot token in the interactions.Client(token='<token>') line before running the bot.
