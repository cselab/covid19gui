#!/usr/bin/env python3

import os
import json
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--dataDir', required=True, help="path to _korali_propagation and _korali_samples")
parser.add_argument('--outfile', required=True, help="Filename for output.")

def unpack(samples):
    rs = []
    xs = []
    for sample in samples:
        r = sample['Saved Results']['Dispersion']
        x = sample['Saved Results']['Variables'][0]['Values']
        rs.append(np.array(r))
        xs.append(np.array(x))


    js = {}
    js['Daily Infections'] = np.array(xs)
    js['Dispersion'] = np.array(rs)
     
    return js


def getRefData(samples):
    ref = samples['Problem']['Reference Data']
    return np.cumsum(ref).tolist()

def compute_plot_intervals(propagatedVariables, varName, llkModel, ns=1000, pct=0.9) :
 
    Np, Nt = propagatedVariables[varName].shape
    Nt = Nt - 4 # FInd out whats going on, I think we propagate into the future in epidemics script
    samples = np.zeros((Np*ns,Nt))

    if llkModel == 'Normal':
      for k in range(Nt):
        m = propagatedVariables[varName][:,k]
        r = propagatedVariables['Standard Deviation'][:,k]
        x = [ np.random.normal(m,r) for _ in range(ns) ]
        samples[:,k] = np.asarray(x).flatten()

    elif llkModel == 'Positive Normal':
      for k in range(Nt):
        m = propagatedVariables[varName][:,k]
        s = propagatedVariables['Standard Deviation'][:,k]
        t = get_truncated_normal(m,s,0,np.Inf)
        x = [ t.rvs() for _ in range(ns) ]
        samples[:,k] = np.asarray(x).flatten()

    elif llkModel == 'Negative Binomial':
      for k in range(Nt):
        m = propagatedVariables[varName][:,k]
        r = propagatedVariables['Dispersion'][:,k]
        p =  m/(m+r)
        try:
          x = [ np.random.negative_binomial(r,1-p) for _ in range(ns) ]
        except:
          print("Error p: {}".format(p))
        samples[:,k] = np.asarray(x).flatten()

    else:
      abort("Likelihood not found in compute_plot_intervals.")


    mean   = np.zeros(Nt)
    median = np.zeros(Nt)
    for k in range(Nt):
      median[k] = np.quantile( samples[:,k],0.5)
      mean[k] = np.mean( samples[:,k] )

    q1 = np.zeros(Nt)
    q2 = np.zeros(Nt)
    for k in range(Nt):
       q1[k] = np.quantile( samples[:,k], 0.5-pct/2)
       q2[k] = np.quantile( samples[:,k], 0.5+pct/2)
    
    samples = np.cumsum(samples,axis=1)
    cmean   = np.zeros(Nt)
    cmedian = np.zeros(Nt)
    for k in range(Nt):
      cmedian[k] = np.quantile( samples[:,k],0.5)
      cmean[k] = np.mean( samples[:,k] )

    cq1 = np.zeros(Nt)
    cq2 = np.zeros(Nt)
    for k in range(Nt):
       cq1[k] = np.quantile( samples[:,k], 0.5-pct/2)
       cq2[k] = np.quantile( samples[:,k], 0.5+pct/2)
 
    js = {}
    
    di = {}
    di['Mean'] = mean.tolist()
    di['Median'] = median.tolist()

    plh = {}
    plh['Percentage']    = pct
    plh['Low Interval']  = q1.tolist()
    plh['High Interval'] = q2.tolist()
    
    di['Intervals'] = [plh]
    js['Daily Infected'] = di
    
    ti = {}
    ti['Mean'] = cmean.tolist()
    ti['Median'] = cmedian.tolist()

    cplh = {}
    cplh['Percentage']    = pct
    cplh['Low Interval']  = cq1.tolist()
    cplh['High Interval'] = cq2.tolist()
  
    
    ti['Intervals'] = [cplh]
 
    js['Total Infected'] = ti
  
    return js


if __name__ == '__main__':
    args = parser.parse_args()
    ddir = args.dataDir
    outfile = os.path.join(ddir, args.outfile)
    propagationFile = os.path.join(ddir, '_korali_propagation/latest')
    samplesFile     = os.path.join(ddir, '_korali_samples/latest')
    
    prop = None
    with open(propagationFile) as f:
        prop = json.load(f)

    samp = None
    with open(samplesFile) as f:
        samp = json.load(f)

    js  = unpack(prop["Samples"])
    ref = getRefData(samp)
    
    intervals = compute_plot_intervals(js, "Daily Infections", "Negative Binomial", 1000, 0.9)
    intervals['x-data'] = list(range(len(ref)))
    intervals['x-axis'] = list(range(len(ref)))
    intervals['y-data'] = ref

    with open(outfile, 'w') as f:
            json.dump(intervals, f)

