
def model_to_csv(model,fname):
    import csv  
    with open('{}.csv'.format(fname), 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(model.get_header())
        data = model.get_data()
        for row in data:
            rows = []
            for val in row:
                rows.append(val)
            spamwriter.writerow(row)