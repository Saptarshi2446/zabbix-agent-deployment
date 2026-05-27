import csv

csv_file = "ansible/inventory/hosts.csv"
inventory_file = "ansible/inventory.ini"

inventory_content = "[zabbix_agents]\n"

with open(csv_file, newline='') as file:

    reader = csv.DictReader(file)

    for row in reader:

        hostname = row['hostname'].strip()
        ip = row['ip'].strip()
        username = row['username'].strip()

        inventory_content += (
            f"{hostname} "
            f"ansible_host={ip} "
            f"ansible_user={username}\n"
        )

with open(inventory_file, "w") as inv_file:
    inv_file.write(inventory_content)

print("Inventory generated successfully")
