# Linux Homework Tasks

## Task 1: Soft Link & Hard Link

### Soft Link

A **soft link**, also called a symbolic link, is a file that points to another file or directory. It stores the path of the original file.

A soft link can be created using:

```bash
ln -s original.txt softlink.txt
```

For example:

```bash
touch file.txt
ln -s file.txt softlink.txt
```

If the original file is deleted, the soft link will no longer work because it points to a file that does not exist.

### Hard Link

A **hard link** is another name for the same file. Both the original file and the hard link point to the same inode and data on the disk.

A hard link can be created using:

```bash
ln original.txt hardlink.txt
```

Example:

```bash
touch file.txt
ln file.txt hardlink.txt
```

If the original file is deleted, the hard link will still contain the data because the data remains available through the hard link.

### Difference Between Soft Link and Hard Link

| Soft Link                             | Hard Link                                |
| ------------------------------------- | ---------------------------------------- |
| Points to the path of another file    | Points to the same inode                 |
| Can point to directories              | Generally cannot be used for directories |
| Can cross different filesystems       | Cannot cross filesystems                 |
| Becomes broken if original is deleted | Still works if original is deleted       |
| Created using `ln -s`                 | Created using `ln`                       |

To delete a link, we can use:

```bash
rm softlink.txt
rm hardlink.txt
```

**Interview answer:** A soft link is a pointer to another file's path, while a hard link is another directory entry pointing to the same inode and data.

---

# Task 2: adduser vs useradd

Both `adduser` and `useradd` are used to create users in Linux, but they work differently.

### useradd

`useradd` is a low-level Linux command used to create a user.

Example:

```bash
sudo useradd testuser
```

It can also be used with options to specify the home directory, shell, groups, etc.

For example:

```bash
sudo useradd -m -s /bin/bash testuser
```

Here:

* `-m` creates the user's home directory.
* `-s` specifies the login shell.

### adduser

`adduser` is a higher-level and more user-friendly utility, commonly available on Debian and Ubuntu systems. It provides an interactive process for creating a user and automatically handles several configuration steps.

Example:

```bash
sudo adduser testuser
```

It asks for the user's password and other optional information.

### Difference

| adduser                             | useradd                               |
| ----------------------------------- | ------------------------------------- |
| Higher-level utility                | Low-level command                     |
| More user-friendly                  | More manual                           |
| Interactive                         | Usually non-interactive               |
| Commonly used on Ubuntu/Debian      | Available on most Linux distributions |
| Automatically handles many defaults | Requires options for some settings    |

### Which is preferred on Ubuntu?

On Ubuntu, **`adduser` is generally preferred for normal user creation** because it is easier to use and handles common user setup automatically.

For example:

```bash
sudo adduser testuser
```

This creates the test user and guides the administrator through the setup.

---

# Task 3: journalctl

`journalctl` is a Linux command used to view and manage logs collected by the **systemd journal**.

It is useful for troubleshooting system problems, checking services, and finding errors.

### View all logs

```bash
journalctl
```

This displays the system journal.

### View the latest logs

```bash
journalctl -e
```

This opens the logs at the most recent entries.

Another useful command is:

```bash
journalctl -n 50
```

It displays the last 50 log entries.

### View logs for the current boot

```bash
journalctl -b
```

This shows logs generated during the current system boot.

### View logs for a specific service

The `-u` option can be used to specify a systemd service.

For example, to check SSH logs:

```bash
sudo journalctl -u ssh
```

To see only recent SSH logs:

```bash
sudo journalctl -u ssh -n 50
```

To follow new log entries as they appear:

```bash
sudo journalctl -u ssh -f
```

The `-f` option works similarly to `tail -f` and continuously displays new log entries.

### Why is journalctl useful?

`journalctl` is useful when diagnosing problems such as:

* Services failing to start
* Boot problems
* Authentication issues
* Network problems
* Application errors
* System crashes

