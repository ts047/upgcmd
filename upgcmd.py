#!/usr/bin/env python

#===================================================================#
#  upgcmd - command line utility to check                           #
#           upgradable package information for apt based system     #
#  Dependencies :-  python 2.7 , python-apt                         #
#  Tarundip Sardar [ dev.ts047@gmail.com ]                          #
#  NOTE : recommends to update the apt cache before use             #
#===================================================================#

import sys
import re
import getopt
try :
    import apt
    import apt_pkg
except ImportError as e:
    print e
    print 'Python-apt must be insatalled...'


s_cache = None
s_pkg_name_list = None
upg_pkg_list = []
priority_list = ['standard', 'important', 'required', 'optional', 'extra']
priority_apt_dict = {
            'standard':[], 
	    'important':[], 
	    'required':[], 
	    'optional':[],
	    'extra':[]
	    }

section_apt_dict = {}

def initializeConfig() :
    ''' populate the apt dictionary 
    and other necesary information'''
    
    global s_cache;
    global s_pkg_name_list;

    s_cache = apt.cache.Cache()
    s_pkg_name_list = s_cache.keys()

    for pkg_name in s_pkg_name_list :
	s_pkg = s_cache[pkg_name]

	if s_pkg.is_upgradable :
	    prt = s_pkg.candidate.priority

            if s_pkg.section in section_apt_dict :
                section_apt_dict[s_pkg.section].append(s_pkg)
            else :
                section_apt_dict.setdefault(s_pkg.section , []).append(s_pkg)

	    priority_apt_dict[prt].append(s_pkg)
            upg_pkg_list.append(s_pkg)



def getSection(pkg):
    return pkg.section

def getPriority(pkg):
    return pkg.candidate.priority

def convertSize(size) :
    _type = ['Byte', 'KB', 'MB', 'GB' ]
    count = 0
    frac = 0.0
    while(size >= 1024) :
        frac = size / 1024.0
	size = size / 1024
	count = count + 1
    return '%.2f %s' % (round(frac,2), _type[count])


def displayFullPackageInformation(name=None, verbose=False) :

    ''' display all the package information possible '''
    try :
        pkg = s_cache[name]

        print 'Package Name : ',pkg.name,  ' -- ',pkg.candidate.summary
        print 'Section :      ','{:<15}'.format(pkg.section)
        print 'Priority :     ','{:<15}'.format(pkg.candidate.priority), '\n'

        print 'Installed : ','{:<40}'.format(pkg.installed.version)
        print 'Candidate : ','{:<40}'.format(pkg.candidate.version)

        print 'Description : \n\t\t%s\n' % (pkg.candidate.description)
        
        if verbose :
            print '\nchangelog :\n'
            print '\t%s\n' % (pkg.get_changelog())
    except KeyError :
        print 'Package name not found !!!!'

def upgradeSummary():
    ''' display the whole upgradable summary information '''

    count_list = []
    d_size_list = []
    i_size_list = []

    total_ds = 0L
    total_is = 0L

    for prio in priority_list :
        pkg_list = priority_apt_dict[prio]
        d_size = 0L
        ins_size = 0L
        count_list.append(len(pkg_list))

        for pkg in pkg_list :
            d_size = d_size + pkg.candidate.size
            ins_size = ins_size + pkg.candidate.installed_size

        total_ds = total_ds + d_size
        total_is = total_is + ins_size

        d_size_list.append(d_size)
        i_size_list.append(ins_size)


    print 'Total number of Upgradable package : %d' % len(upg_pkg_list)
    print 'Download size : %s' % (convertSize(total_ds))
    print 'Installed Size : %s' % (convertSize(total_is))

    print '-' * 40        
    print '{:<15}'.format('Priority'), \
	  '{:<5}'.format('Count'), \
	  '{:<10}'.format('Download'), \
	  '{:<10}'.format('Installed Size')
    print '-' * 40


    for i in range(len(count_list)) :
	print '{:<15}'.format(priority_list[i]), \
	      '{:<5}'.format(str(count_list[i])), \
	      '{:<10}'.format(convertSize(d_size_list[i])), \
	      '{:<10}'.format(convertSize(i_size_list[i]))
    


def listPackageByPriority(priority=None, outfile=None) :

    ''' list all the package name based on priority
    if outfile given then dump '''
    
    try :
        out = None
        if outfile is not None :
            out = open(outfile, 'w')

        if priority is None :
                pkg_list = upg_pkg_list
                for pkg in pkg_list :
                    if outfile is not None :
                        out.write(pkg.name)
                    else :
                        print pkg.name
                

        else :
            _list = priority_apt_dict[priority]
            pkg_list = sorted(_list, key=getSection)
            for pkg in pkg_list :
                if out is not None :
                    out.write(pkg.name+'\n')
                else :
                    print pkg.name
            
        if out is not None :
            out.close()

    except Exception as e :
        print e
        sys.exit(1)

def listPackageBySection(section=None, outfile=None) :

    ''' list all the package name based on section
    if outfile given then dump '''

    try :
        out = None
        if outfile is not None :
            out = open(outfile, 'w')

        if section is None :
            for key in section_apt_dict.keys() :
                pkg_list = section_apt_dict[key]
                for pkg in pkg_list :
                    if outfile is not None :
                        out.write(pkg.name)
                    else :
                        print pkg.name
                

        else :
            if section in section_apt_dict.keys() :
                _list = section_apt_dict[section]
                pkg_list = sorted(_list, key=getPriority)
                for pkg in pkg_list :
                    if out is not None :
                        out.write(pkg.name+'\n')
                    else :
                        print pkg.name
            
        if out is not None :
            out.close()
    except Exception as e:
        print e
        sys.exit(1)

def listPackageByPrioritySection(priority=None, section=None,  outfile=None) :

    ''' list all the package name based on priority and section given
    if outfile given then dump '''

    try :
        out = None
        if outfile is not None :
            out = open(outfile, 'w')

        if priority is None :
                pkg_list = upg_pkg_list
                for pkg in pkg_list :
                    if pkg.section == section :
                        if outfile is not None :
                            out.write(pkg.name)
                        else :
                            print pkg.name
                

        else :
            _list = priority_apt_dict[priority]
            for pkg in _list :
                if pkg.section == section :
                    if out is not None :
                        out.write(pkg.name+'\n')
                    else :
                        print pkg.name
            
        if out is not None :
            out.close()

    except Exception as e:
        print e
        sys.exit(1)

def listUpdateByRegex(regex, section=None, priority=None, outfile=None) :
    ''' display all the upgrade able packge by regular expression
    section priority '''

    try :
        out = None
        if outfile is not None :
            out = open(outfile, 'w')

        rcom = re.compile(regex)
        pkg_list = []

        for pkg in upg_pkg_list:
            if rcom.match(pkg.name) :
                if priority :
                    if pkg.candidate.priority == priority :
                        if section :
                            if pkg.section == section :
                                pkg_list.append(pkg)
                        else :
                            pkg_list.append(pkg)
                else :
                    if section :
                        if pkg.section == section :
                            pkg_list.append(pkg)
                    else :
                        pkg_list.append(pkg)

        for i in pkg_list :
            if out :
                out.write(i.name+'\n')

            else :
                print i.name

        if out is not None:
            out.close()

    except Exception as e:
        print e
        sys.exit(1)



def displayPackageByPriority(priority=None, section=False) :

    ''' Display the upgradable package as per given "priority"
    if "section" parameter is given , sorted by package section
    '''

    length = 135
    print "-" * length
    print '{:<25}'.format('PACKAGE'), \
	  '{:<15}'.format('SECTION'), \
	  '{:<25}'.format('INSTALLED'), \
	  '{:<25}'.format('CANDIDATE'), \
	  '{:>8}'.format('SIZE')

    print "-" * length

    if priority is None and priority not in priority_apt_dict.keys() :
        print "Invalid priority ..."

    p_list = priority_apt_dict[priority]
    size = 0
   
    if section is True:
	pkg_list = sorted(p_list, key=getSection)

    for pkg in pkg_list :
	print '{:<25}'.format(pkg.name), \
	      '{:<15}'.format(pkg.section), \
	      '{:<25}'.format(pkg.installed.version), \
	      '{:<25}'.format(pkg.candidate.version), \
	      '{:>10}'.format(convertSize(int(pkg.candidate.size))), \
                '\t',pkg.candidate.summary

	size = size + int(pkg.candidate.size)
    print "-" * length

    return size, len(pkg_list)

def displayPackageBySection(section=None) :

    ''' Display the upgradable package as per given "section"
    '''

    length = 135
    print "-" * length
    print '{:<25}'.format('PACKAGE'), \
	  '{:<15}'.format('SECTION'), \
	  '{:<25}'.format('INSTALLED'), \
	  '{:<25}'.format('CANDIDATE'), \
	  '{:>8}'.format('SIZE')

    print "-" * length

    if section is None :
        print " Invalid section ..."
    pkg_list = section_apt_dict[section]
    size = 0

    for pkg in pkg_list :
	print '{:<25}'.format(pkg.name), \
	      '{:<15}'.format(pkg.section), \
	      '{:<25}'.format(pkg.installed.version), \
	      '{:<25}'.format(pkg.candidate.version), \
	      '{:>10}'.format(convertSize(int(pkg.candidate.size))), \
                '\t',pkg.candidate.summary

	size = size + int(pkg.candidate.size)
    print "-" * length

    return size, len(pkg_list)


def listSecurityUpdate(priority='all') :

    ''' show all security update based on priority level 
    keyword here is "SECURITY UPDATE"
    '''

    pkg_list = priority_apt_dict[priority]
    sec_pkg_cl = {}
    for pkg in pkg_list :
        cl = pkg.get_changelog()
        pkg.cl = cl    # modifying the pkg struct for future faster changelog usage

        if len(re.findall('SECURITY UPDATE', cl)) > 0 :
            sec_pkg_cl[pkg.name] = cl
            print pkg.name  # only for debugging purpose
            print cl

    return sec_pkg_cl



def print_usage() :

    usage = """    
    -s, --section   SECTION         Section wise show packages
    -v, --verbose                   More verbosity in the report message 
    -p, --priority  PRIORITY        Priority wise show packages
                                    PRIORITY ::= important | standard | required | optional | extra 
    -o, --output    FILE            Dump to the FILE
    -h, --help                      Display this help message 
    -c, --changelog PACKAGE         Show the changelog of PACKAGE
        --package   PACKAGE         Show the full package information of PACKAGE
        --summary                   Print summary information of current upgradable packages""" 
    print usage

def main(argv) :
    ''' main function '''

    PRIORITY = None
    OUTFILE = None
    VERBOSE = 0
    SUMMARY = None
    PKG_NAME = None
    SECTION = None
    REGEX = None
    CL = None

    try :
        options, command = getopt.getopt(argv, 'c:vhp:o:s:', \
                                            ['priority=' \
                                            ,'changelog=' \
                                            ,'help' \
                                            ,'verbose' \
                                            ,'package=' \
                                            ,'regex=' \
                                            ,'section=' \
                                            ,'summary' \
                                            ,'output='])
    except getopt.GetoptError as err :
        print str(err)
        print_usage()
        sys.exit(2)

    for opt, arg in options :

        #help 
        if opt in (['-h', '--help']) :
            print_usage()
            sys.exit()

        #summary
        if opt in (['--summary']) :
            SUMMARY = 1
        
        #section
        if opt in (['-s','--section']) :
            SECTION = arg
            if SECTION is None :
                print_usage()
                sys.exit(1)

        #changelog
        if opt in (['-c','--changelog']):
            CL = arg
            if CL is None :
                print_usage()
                sys.exit(1)

        #priority
        if opt in (['-p', '--priority']) :
            PRIORITY = arg
            if PRIORITY is None or arg not in priority_list :
                print_usage()
                sys.exit(1)

        #outfile
        if opt in (['-o', '--output']) :
            OUTFILE = arg
            if OUTFILE is None :
                print_usage()
                sys.exit(1)

        #verbose 
        if opt in (['-v', '--verbose']) :
            VERBOSE = 1

        #package information
        if opt in (['--package']):
            PKG_NAME = arg
            if PKG_NAME is None :
                print_usage()
                sys.exit(1)

        # regex option
        if opt in (['--regex']) :
            REGEX = arg
            if REGEX is None :
                print_usage()
                sys.exit(1)

    
    initializeConfig()

    if SUMMARY : 
        upgradeSummary()
        sys.exit(1)

    elif REGEX :
        listUpdateByRegex(REGEX, SECTION, PRIORITY, OUTFILE)

    elif CL :
        displayFullPackageInformation(CL, True)

    elif PKG_NAME and VERBOSE :
        displayFullPackageInformation(PKG_NAME, True)

    elif PKG_NAME:
        displayFullPackageInformation(PKG_NAME)

    elif PRIORITY and SECTION :
        listPackageByPrioritySection(PRIORITY, SECTION, OUTFILE)

    elif PRIORITY and VERBOSE :
        displayPackageByPriority(PRIORITY, True)
    
    elif PRIORITY :
        listPackageByPriority(PRIORITY, OUTFILE)

    elif SECTION and VERBOSE :
        displayPackageBySection(SECTION)

    elif SECTION :
        listPackageBySection(SECTION, OUTFILE)

    else :
        print_usage()


if __name__ == "__main__" :
        main(sys.argv[1:])
