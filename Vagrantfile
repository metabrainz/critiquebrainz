# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provision :shell, path: "scripts/bootstrap.sh"

  config.vm.network "forwarded_port", guest: 5000, host: 5000
  
  # PostgreSQL
  config.vm.network "forwarded_port", guest: 5432, host: 15432
end
