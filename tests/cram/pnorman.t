  $ [ "$0" != "/bin/bash" ] || shopt -s expand_aliases
  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ alias make_changeset="$PYTHON $TESTDIR/../../make_changeset.py"

  $ make_changeset 12791986
  Namespace(api_url='http://api.openstreetmap.org/', changeset=12791986, replicate_period=60.0, replication_url='http://planet.osm.org/redaction-period/minute-replicate/', retry=5)
  Found changeset 12791986 by pnorman (355617)
  Changeset spans 2012-08-20T06:49:50Z to 2012-08-20T07:50:13Z
  Sequence range is 196813 to 196878
  Parsing 196813
  Parsing 196814
  Parsing 196815
  Parsing 196816
  Parsing 196817
  Parsing 196818
  Parsing 196819
  Parsing 196820
  Parsing 196821
  Parsing 196822
  Parsing 196823
  Parsing 196824
  Parsing 196825
  Parsing 196826
  Parsing 196827
  Parsing 196828
  Parsing 196829
  Parsing 196830
  Parsing 196831
  Parsing 196832
  Parsing 196833
  Parsing 196834
  Parsing 196835
  Parsing 196836
  Parsing 196837
  Parsing 196838
  Parsing 196839
  Parsing 196840
  Parsing 196841
  Parsing 196842
  Parsing 196843
  Parsing 196844
  Parsing 196845
  Parsing 196846
  Parsing 196847
  Parsing 196848
  Parsing 196849
  Parsing 196850
  Parsing 196851
  Parsing 196852
  Parsing 196853
  Parsing 196854
  Parsing 196855
  Parsing 196856
  Parsing 196857
  Parsing 196858
  Parsing 196859
  Parsing 196860
  Parsing 196861
  Parsing 196862
  Parsing 196863
  Parsing 196864
  Parsing 196865
  Parsing 196866
  Parsing 196867
  Parsing 196868
  Parsing 196869
  Parsing 196870
  Parsing 196871
  Parsing 196872
  Parsing 196873
  Parsing 196874
  Parsing 196875
  Parsing 196876
  Parsing 196877


  $ mkdir minute
  $ sed 's/^[ ]*//g' *osc > 12791986.osc.tmp
  $ mv 12791986.osc.tmp 12791986.osc
  $ mv *osc minute

Test use w/ hourly replication diffs:

  $ make_changeset --replication-url=http://planet.osm.org/redaction-period/hour-replicate/ 12791986
  Namespace(api_url='http://api.openstreetmap.org/', changeset=12791986, replicate_period=3600.0, replication_url='http://planet.osm.org/redaction-period/hour-replicate/', retry=5)
  Found changeset 12791986 by pnorman (355617)
  Changeset spans 2012-08-20T06:49:50Z to 2012-08-20T07:50:13Z
  Sequence range is 3309 to 3311
  Parsing 3309
  Parsing 3310

  $ mkdir hour
  $ sed 's/^[ ]*//g' *osc > 12791986.osc.tmp
  $ mv 12791986.osc.tmp 12791986.osc
  $ mv *osc hour

Extract stored, correct output

  $ mkdir correct
  $ tar xzf $TESTDIR/pnorman-out.tar.gz -C correct
  $ sed 's/^[ ]*//g' correct/*osc > correct/12791986.osc.tmp
  $ mv correct/12791986.osc.tmp correct/12791986.osc

Compare pre-computed output to what we just generated

  $ diff -uNr correct minute
  $ diff -uNr correct hour
