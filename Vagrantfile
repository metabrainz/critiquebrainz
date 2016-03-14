# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "hashicorp/precise64"

  config.vm.provision :shell, path: "admin/bootstrap.sh"

  config.vm.network "forwarded_port", guest: 8080, host: 8080

  # PostgreSQL
  config.vm.network "forwarded_port", guest: 5432, host: 15432
end
