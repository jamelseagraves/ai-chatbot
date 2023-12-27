# ai-chatbot

This is a Q&A chatbot that you can run and ask questions about information from Wikipedia.

See detailed design documentation [here](https://github.com/jamelseagraves/ai-chatbot/blob/main/Q%26A%20AI%20Chatbot%20Design.pdf)

## Prerequisites
- Python 3.6+
- Pip3

## How to use
First, you will need to install Postgres and run a data server with a database.
For Mac users:
* Option 1: You can download and install [Postgres.app](https://postgresapp.com/downloads.html). Launch the app and click "Initialize" to start a data server. A database will automatically be created for you.
* Option 2: Install Postgres with Homebrew
  * `brew install postgresql`
  * `brew services start postgresql`

Then you need to clone (or download) this repository, go to the root directory of this project on your machine, and run `pip3 install -r requirements.txt`.

Run `python3 ./data_loader.py <dbname>` first to load the data in the database. As output, you should see a list of titles of Wikipedia pages that you can ask questions about with the CLI.

Finally, run `python3 ./cli.py <dbname>` to start the CLI, and it should prompt you to start asking questions.

You can try some questions like:
- What is Anarchism?
- What is Aristotle famous for?
- Who was Achilles' mother?
- Who was Thetis?

**Note:** If you want to load more topics (Wikipedia pages) in the database, you can modify this [code line](https://github.com/jamelseagraves/ai-chatbot/blob/164632f870ffaa0ffc7b6c58b1749c8f0f2df6dd/data_loader.py#L65) before running `data_loader.py`.
