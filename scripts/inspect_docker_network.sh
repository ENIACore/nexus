#!/bin/bash
# Inspect networks of container

echo "Enter name of container to inspect"
read container_name

docker inspect $container_name --format='{{range $net, $config := .NetworkSettings.Networks}}{{$net}}: {{$config.IPAddress}}{{"\n"}}{{end}}'
