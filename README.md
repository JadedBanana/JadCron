# JadCron

JadCron is a python-based task scheduler made by Jade Godwin for Windows. How it works is, once a minute, the program will load in all the config files in the program directory and parse them. Then it will run a command with arguments and so on and so forth. It's basically like cronjobs but for windows and it goes less often.

---

## Startup

Jadcron is best used when it is run on startup in the background.

1. Press Windows + R to open the "Run" dialog box.
1. Type `shell:startup` and hit Enter to open the "Startup" folder.
1. Create a shortcut to either `jadcron.bat` or `jadcron_background.vbs` in this folder.
  - `jadcron_background.vbs` will have the program run in the background. This is recommended.
  - `jadcron.bat` will have the console up when running. Always.

Now JadCron will run on startup.

---

## Config Files

Config files are written in json and are all stored in the same folder as the program. Here's an example:

```json
{
    "command": "open webpage",
    "args": "http://google.com",
    "run options": {
        "weekday": "wednesday",
        "delay mode": "weekly",
        "run if chance passed": true
    },
    "last run": {
        "year": 2019,
        "month": 7,
        "day": 31,
        "hour": 11,
        "minute": 15
    }
}
```

The keys are split into three groups:

1. [Required Keys](#Required-Keys)
2. [Optional Keys](#Optional-Keys)
3. [System Keys](#System-Keys)

But the most important part is the commands and the arguments:
- [Valid Commands](#Valid-Commands)
- [Arguments](#Arguments)

---

## Required Keys

There are two required keys for every config file that are pretty much the essence of what this program is all about:

- `"command"`: Stores program command(s). These are written as either strings or as list of strings. The list allows for commands to be run sequentially rather than simultaneously as they would when split into separate config files.
- `"args"`: Stores command arguments. This can be literally any valid data type for json. If the configuration uses more than one command, the args should be an array of arguments per command.

---

## Optional Keys

There are multiple optional keys that are useful for scheduling:

- `"run options"`: Has the run options for the command. It has a number of sub-keys, none of which are required.
  - `"year"`: The year(s) the command should run in.
  - `"month"`: The month(s) the command should run in. Runs from 1 to 12.
  - `"weekday"`: The weekday(s) the command should run on. Runs from 0 to 6 (0 is Monday).
  - `"day"`: The day(s) the command should run in. Runs from 1 to 31.
  - `"hour"`: The hour(s) the command should run in. Runs from 0 to 23.
  - `"minute"`: The minute(s) the command should run in. Runs from 0 to 59.
    - All six of the previous keys use the exact same style of parameters (all of these are valid so long as you replace the numerical values with those for the data type):
      - `2019` and `"2019"` mean just one year.
      - `[2019, 2020, 2022, ...]` and `["2019", "2020", "2022", ...]` mean a set of years.
      - `"2009-"`, "`2008 - 2029"`, and `"-2029"` mean a range of years.
      - `["2009-2011", "2016-2020", ...]` means a set of ranges of years.
    - `"month"` and `"weekday"` can also be written as `"january"`, `"march"`, etc. and `"monday"`, `"friday"`, etc. respectively.
  - `"delay mode"`: Has the delay mode for the program. If it is not set, the program will just run every time the other run options allow it. Its possible values are as following:
    - `null`: Runs literally every moment it can.
    - `"yearly"`: Runs as soon as possible once the year of the previous run doesn't equal the current year.
    - `"{n} year(s) passed"`: Runs as soon as possible once n years have passed since the previous run.
    - `"monthly"`: Runs as soon as possible once the month of the previous run doesn't equal the current month.
    - `"{n} month(s) passed"`: Runs as soon as possible once n months have passed since the previous run.
    - `"last month day"`: Will run on the last day of the month.
    - `"weekly"`: Runs as soon as possible once the week of the previous run doesn't equal the current week.
    - `"{n} week(s) passed"` Runs as soon as possible once n weeks have passed since the previous run.
    - `"daily"`: Runs as soon as possible once the day of the previous run doesn't equal the current day.
    - `"{n} day(s) passed"` Runs as soon as possible once n days have passed since the previous run.
    - `"hourly"`: Runs as soon as possible once the hour of the previous run doesn't equal the current hour.
    - `"{n} hour(s) passed"`: Runs as soon as possible once n hours have passed since the previous run.
    - `"once"`: Will run once then never again.
    - For any value with `{n}` in it, that can be totally left out to just equal 1.
  - `"run if chance passed"`: A boolean value that stores whether or not the program should run as soon as possible once the delay mode has fulfilled its purpose, even if the other run options don't apply.
    - This is useful for if the program is set to run on the first of the month or something but it, for whatever reason, can't run until the second. Basically, if it missed an opportunity to run.
  - `"random chance"`: A float value that pretty much establishes a random chance the command will run at any given minute where it can otherwise.
    - 1 is 100% and 0.05 is 5%. You get the gist.
    - This is great for pranks! Keep in mind, though, that this program runs once a minute, so keep your chances low as to not set off any alarms.
- `"output file"`: The locale for the output file. If not inluded, it will just be a file with the same name plus ".output.txt" tacked on the end. If not set to a string, it the output file will not be generated.
- `"args function prefix"`: The prefix for mid-argument functions and variables. Is set to `"?:>"` by default.

---

## System Keys

These kays are really only used by the program and you don't really need to bother yourself with them:

- `"last run"`: Stores the time and date the config file's command was last run. It's used for messing with the delay mode and running if the chance has passed. It has a number of sub-keys, all of which are required if this key is in the config file.
  - `"year"`: The year the command was last run.
  - `"month"`: The month the command was last run.
  - `"day"`: The day the command was last run.
  - `"hour"`: The hour the command was last run.
  - `"minute"`: The minute the command was last run.


## Valid Commands

- File Operations
  - [`"create backup"`](#create-backup)
  - [`"copy file"`](#copy-file)
  - [`"append file"`](#append-file)
  - [`"overwrite file"`](#overwrite-file)
  - [`"delete file"`](#delete-file)
- Webpage Operations
  - [`"open webpage`](#open-webpage)
- Hardware Simulation
  - [`"simulate mouse"`](#simulate-mouse)
- Misc.
  - [`"sleep"`](#sleep)
  - [`"do nothing"`](#do-nothing)

This is all the commands in their bulleted list.

- `"create backup"`: Creates a backup of a file(s) or folder(s).<a name="create-backup"></a>
  - `"args"` for this one should be a list with the following attributes:
    - `{source_file_or_folder}`: The source file(s) or folder(s). This can be either a string ot a list of strings. Can use either forward or backward slashes.
    - `{destination_folder}`: The desetination folder(s). This can be either a string or a list of strings. Can be either forward or backward slashes.
    - `{detailed_output} = false`: Determines whether or not the output is detailed. This is a bool value and is false by default.
    - `{keep_attributes} = true`: Determines whether or not to keep the attributes of the files copied. This is a bool value and is true by default.
  - Note that though both the source and destination folders can be lists, this will copy all the original file(s) or folder(s) to every single destination folder.
  - If the destination folder is inside the source folder, the destination folder will not be copied over.
  - Examples:

    ```json
    {
        "command": "create backup",
        "args": [
            "C:/Projects/MajorBigProject",
            "C:/Projects/MajorBigProject_BACKUP",
            true
        ],
        "run options": {
            "weekday": "sunday"
        }
    }
    ```

    ```json
    {
        "command": "create backup",
        "args": [
            [
                "C:/Projects/MajorBigProject",
                "C:/Projects/IttyBittyProjectFile.py"
            ],
            [
                "C:/Projects/MajorBigProject_BACKUP",
                "D:/PROJECT_BACKUP_2"
            ],
            false,
            false
        ],
        "run options": {
            "weekday": "sunday"
        }
    }
    ```

- `"copy file"`: Copies a singular file from one location to another.<a name="copy-file"></a>
  - `"args"` for this one should be a list with the following attributes:
    - `{source_file}`: The source file. This is a string. Can use either forward or backward slashes.
    - `{destination_file_or_folder}`: The desetination file(s) or folder(s). This can be either a string or a list of strings. Can be either forward or backward slashes.
    - `{keep_attributes} = true`: Determines whether or not to keep the attributes of the files copied. This is a bool value and is true by default.
  - Note that he destination folder can be a list. This will copy the source file to every single destination file or folder.
  - Examples:

    ```json
    {
        "command": "copy file",
        "args": [
            "C:/Users/You/Pictures/Image_I_Keep_Deleting.jpeg",
            "C:/Users/You/Desktop"
        ]
    }
    ```

    ```json
    {
        "command": "copy file",
        "args": [
            "C:/Users/You/Pictures/Image_I_Keep_Deleting.jpeg",
            [
                "C:/Users/You/Desktop",
                "C:/Users/You/Documents"
            ],
            true
        ]
    }
    ```
    
- `"append file"`: Appends text to the end of an already existing file.<a name="append-file"></a>
  - `"args"` for this one should be a list with the following attributes:
    - `{file_to_write}`: The file to be written to. This is a string. Can use either forward or backward slashes.
    - `{text_to_write}`: The text to be written in the file. Doesn't matter what kind of data this is, it will always be turned into a string.
  - The file to write can be a list, in which case multiple files will be written to.
  - Examples:
    
    ```json
    {
        "command": "append file",
        "args": [
            "C:/Users/You/Documents/My_File.txt",
            "Today's date is ?:>>year()-?:>>month()-?:>>day()\n"
        ],
        "run options": {
            "delay mode": "2 days passed"
        }
    }
    ```

    ```json
    {
        "command": "append file",
        "args": [
            [
                "C:/Users/You/Documents/My_File.txt",
                "C:/Backup/My_File.txt"
            ],
            "Hello, world, from ?:>>year()!"
        ],
        "run options": {
            "delay mode": "yearly"
        }
    }
    ```

- `"overwrite file"`: Overwrites a file and writes something new. Exactly like `"append file"` except it deletes the file's original contents before writing.<a name="overwrite-file"></a>
  - `"args"` for this one should be a list with the following attributes:
    - `{file_to_write}`: The file to be written to. This is a string. Can use either forward or backward slashes.
    - `{text_to_write}`: The text to be written in the file. Doesn't matter what kind of data this is, it will always be turned into a string.
  - The file to write can be a list, in which case multiple files will be written to.
  - Examples:
    
    ```json
    {
        "command": "overwrite file",
        "args": [
            "C:/Users/You/Documents/My_File.txt",
            "Last updated ?:>>year()-?:>>month()-?:>>day()\n"
        ],
        "run options": {
            "delay mode": "2 days passed"
        }
    }
    ```

    ```json
    {
        "command": "overwrite file",
        "args": [
            [
                "C:/Users/You/Documents/My_File.txt",
                "C:/Backup/My_File.txt"
            ],
            "This year is ?:>>year()"
        ],
        "run options": {
            "delay mode": "yearly"
        }
    }
    ```

- `"delete file"`: Deletes a file or folder.<a name="delete-file"></a>
  - `"args"` for this one should be either a string or a list representing files/folders to be deleted. Can use either forward or backward slashes.
  - Examples:
  
    ```json
    {
        "command": "delete file",
        "args": ["C:/Users/You/Desktop/unwanted.log", "C:/Users/You/Desktop/unwanted (2).log"
    }
    ```
  
    ```json
    {
        "command": "delete file",
        "args": "C:/Folder_That_Needs_Deletion"
    }
    ```

- `"open webpage"`: Opens a webpage.<a name="open-webpage"></a>
  - `"args"` for this one should be either a string representing the URL of a webpage or a list of strings representing webpages.
  - If the URL doesn't start with `http://`, `https://`, `localhost:`, or a number, the program will automatically make it start with `http://`.
  - Examples:

    ```json
    {
        "command": "open webpage",
        "args": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "run options": {
            "random chance": 0.0005
        }
    }
    ```

    ```json
    {
        "command": "open webpage",
        "args": [
            "reddit.com",
            "youtube.com",
            "netflix.com"
        ],
        "run options": {
            "delay mode": "daily"
        }
    }
    ```
    
- `"simulate mouse"`: Simulates the mouse.
  - `"args"` is a string or a list of strings that represent mouse operations. These strings should be one of the following:
    - `"setpos(x, y)"`: Move the mouse to position `(x, y)`.
    - `"move(x, y)"`: Move the mouse `(x, y)` pixels across the screen.
    - `"click(button, amount=1)"`: Click a mouse button `amount` number of times.
    - `"press(button)"`: Press a mouse button.
    - `"release(button)"`: Release an already pressed mouse button.
    - `"scroll(dy)"`: Scroll the scroll wheel the specified amount. Be aware, these numbers are a lot bigger than you think they are.
    - `"scroll(dx, dy)"`: Scroll the scroll wheel the specified amount. Be aware, these numbers are a lot bigger than you think they are.
    - Note that the arguments for every command should be ints.
      - `button` has three values: 0 for left, 1 for right, and 2 for middle.
  - Example:
  
    ```json
    {
        "command": "simulate mouse",
        "args": [
            "move(800, 600)",
            "click(0, 2)",
            "setpos(500, 0)",
            "press(0)",
            "move(0, 80)",
            "release(0)"
        ],
        "run options": {
            "minute": 0,
            "hour": "10-14"
        }
    }
    ```
    
- `"sleep"`: Pauses the program for a set amount of seconds.<a name="sleep"></a>
  - `"args: {amount_of_seconds}"`
  - This is really only useful if you're running commands sequentially.
  - Example:

    ```json
    {
        "command": [
            "open webpage",
            "sleep",
            "open webpage"
        ],
        "args": [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            7200,
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ],
        "run options": {
            "random chance": 0.0005
        }
    }
    ```
    
- `"do nothing"`: Does nothing. Literally, that's it.<a name="do-nothing"></a>
  - `"args"` can be literally anything. Args are not needed to do nothing.
  - This is more a debug command than anything. You're welcome to use it, but it literally does nothing.
  - Example:

    ```json
    {
        "command": "do nothing",
        "args": null
    }
    ```
