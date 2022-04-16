kill -9 $(sudo lsof -t -i:5000)
kill -9 $(sudo lsof -t -i:5001)

service postgresql restart
cd /var/www/nop
{
    sleep 3
    xdg-open http://localhost:5000
}&
sudo dotnet --fx-version 6.0.4 Nop.Web.dll
