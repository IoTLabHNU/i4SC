import mysql.connector;
import time;

#Connection MySQL
cnx = mysql.connector.connect(user='pi2', password='password',
                              host='10.49.63.147',
                              port='3306',
                              database='Scale2'
                              );

try:
     cursor = cnx.cursor();
     query = "INSERT INTO Test (zeit,weight) VALUES (%s, %s)";
     tval=time.strftime('%Y-%m-%d %H:%M:%S')
     print (tval)
     vals = (tval,weight,);
     result = cursor.execute(query, vals)
     cnx.commit();
except:
     print("nix gut")
cursor.close();


