Exec { path => [ "/bin/", "/sbin/", "/usr/bin/", "/usr/sbin/", "/usr/local/bin/" ] }

define line($file, $line, $ensure = 'present') {
    case $ensure {
        default : { err ( "unknown ensure value ${ensure}" ) }
        present: {
            exec { "/bin/echo '${line}' >> '${file}'":
                unless => "/bin/grep -qFx '${line}' '${file}'"
            }
        }
        absent: {
            exec { "/bin/grep -vFx '${line}' '${file}' | /usr/bin/tee '${file}' > /dev/null 2>&1":
              onlyif => "/bin/grep -qFx '${line}' '${file}'"
            }

            # Use this resource instead if your platform's grep doesn't support -vFx;
            # note that this command has been known to have problems with lines containing quotes.
            # exec { "/usr/bin/perl -ni -e 'print unless /^\\Q${line}\\E\$/' '${file}'":
            #     onlyif => "/bin/grep -qFx '${line}' '${file}'"
            # }
        }
    }
}

class repo {
    include smarthouse

    exec { 'repo-clone':
        command => "sudo -u aiko git clone git://github.com/antigluk/pySmartHouse.git",
        cwd     => "/home/aiko",
        require => [User['aiko'], Package['git']],
        onlyif => "test ! -d /home/aiko/pySmartHouse",
    }

    exec { 'repo-pull':
        command => "sudo -u aiko git pull origin master",
        cwd     => "/home/aiko/pySmartHouse",
        require => [User['aiko'], Package['git']],
        unless => "test ! -d /home/aiko/pySmartHouse",
        notify => Service['smarthouse'],
    }
}

class smarthouse {
    include repo

    user { 'aiko':
        ensure => present,
        managehome => true,
        groups => 'admin',
        shell => '/bin/bash',
        require => Group['admin'],
    }

    group { 'admin':
        ensure => present,
    }

    package {'git':
        ensure => installed,
    }

    exec { 'submodules':
        command => "sudo -u aiko git submodule update --init",
        cwd     => "/home/aiko/pySmartHouse",
        require => Class['repo'],
    }

    exec { 'aiko-pass':
        command => "sudo passwd aiko << EOF\naiko\naiko\nEOF",
        onlyif => "egrep -q '^aiko:*:' /etc/shadow",
        require => User[aiko],
    }

    exec { 'github-keys':
        command => "cp -r /vagrant/ssh /home/aiko/.ssh && chown aiko:aiko -R /home/aiko/.ssh",
        onlyif => "test -d ",
        require => User[aiko],
    }

    file { '/etc/udev/rules.d/70-persistent-net.rules':
        ensure => directory,
    }

    line { network_hostonly:
        file => "/etc/network/interfaces",
        line => "iface eth1 inet dhcp",
    }

    package { 'mplayer':
        ensure => installed,
    }

    package { 'imagemagick':
        ensure => installed,
    }

    include frontend
}

class frontend {
    include smarthouse

    file { '/home/aiko/frontend':
        ensure => link,
        target => '/home/aiko/pySmartHouse/web-frontend',
        require => Class['smarthouse'],
    }

    file { '/home/aiko/static':
        ensure => link,
        target => '/home/aiko/pySmartHouse/resources/static',
        require => Class['smarthouse'],
    }

    package { 'python-pip':
        ensure => installed,
    }

    exec {'virtualenv':
        command => 'pip install virtualenv',
        require => Package['python-pip'],
    }

    exec {'env':
        command => 'virtualenv /home/aiko/pySmartHouse/web-frontend/.env',
        require => Exec['virtualenv'],
        onlyif => 'test ! -d /home/aiko/pySmartHouse/web-frontend/.env',
    }

    package { 'lm-sensors':
        ensure => installed,
    }

    exec {'pip install':
        command => '/home/aiko/pySmartHouse/web-frontend/.env/bin/pip install flask sh PySensors pyserial',
        require => [Exec['env'], Package['lm-sensors']],
    }

    exec {'sqlite3dbm':
        command => '/home/aiko/pySmartHouse/web-frontend/.env/bin/pip install -e /home/aiko/pySmartHouse/3rdparty/sqlite3dbm',
        require => [Exec['env'], Class['smarthouse']],
    }


    package {'libapache2-mod-wsgi':
        ensure => installed,
    }

    package { 'apache2':
        ensure => installed,
        require => Package['libapache2-mod-wsgi']
    }

    file { 'apache-site':
        path => '/etc/apache2/sites-available/smarthouse',
        ensure => file,
        content => template('/vagrant/smarthouse.apacheconf'),
        require => Package['apache2'],
    }

    exec {'a2ensite smarthouse':
        require => File['apache-site'],
        notify => Service['apache2'],
    }

    service { 'apache2':
        ensure => running,
        enable => true,
        require => Package['apache2'],
    }

    file { '/etc/smarthouse.conf':
        ensure => file,
        content => template('/vagrant/smarthouse.conf'),
    }

}


class watchd {
    file { '/home/aiko/watch':
        ensure => link,
        target => '/home/aiko/pySmartHouse/watch',
    }

    file { '/home/aiko/watchd':
        ensure => link,
        target => '/home/aiko/pySmartHouse/watch/watchd',
    }

    file { 'init-smarthouse':
        path => '/etc/init.d/smarthouse',
        ensure => file,
        content => template('/vagrant/smarthouse'),
        mode => 0755,
    }

    service { 'smarthouse':
        ensure => running,
        enable => true,
        require => File['init-smarthouse'],
    }

}


include frontend
include watchd
