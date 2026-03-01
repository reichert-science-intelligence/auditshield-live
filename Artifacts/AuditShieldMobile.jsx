import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Clock, TrendingUp, FileText, Users } from 'lucide-react';

// Sample data - in production would come from API
const generateSampleCharts = () => {
  const measures = [
    { code: 'CBP', name: 'Blood Pressure Control', weight: 3.0 },
    { code: 'BCS', name: 'Breast Cancer Screening', weight: 3.0 },
    { code: 'COL', name: 'Colorectal Screening', weight: 3.0 },
    { code: 'CDC', name: 'Diabetes Care', weight: 3.0 },
    { code: 'KED', name: 'Kidney Health', weight: 1.0 }
  ];
  
  const riskLevels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  const riskDistribution = { CRITICAL: 100, HIGH: 136, MEDIUM: 19, LOW: 390 };
  
  const charts = [];
  let chartNum = 1;
  
  riskLevels.forEach(risk => {
    for (let i = 0; i < riskDistribution[risk]; i++) {
      const measure = measures[Math.floor(Math.random() * measures.length)];
      charts.push({
        id: `C${String(chartNum).padStart(6, '0')}`,
        memberId: `M${String(Math.floor(Math.random() * 411) + 1).padStart(6, '0')}`,
        measure: measure.code,
        measureName: measure.name,
        riskLevel: risk,
        complianceScore: risk === 'LOW' ? 95 : risk === 'MEDIUM' ? 72 : risk === 'HIGH' ? 45 : 35,
        failureProbability: risk === 'LOW' ? 0.05 : risk === 'MEDIUM' ? 0.28 : risk === 'HIGH' ? 0.65 : 0.85,
        starImpact: (risk === 'LOW' ? 0.0005 : risk === 'MEDIUM' ? 0.002 : risk === 'HIGH' ? 0.003 : 0.004).toFixed(4),
        missingElements: risk === 'LOW' ? [] : risk === 'MEDIUM' ? ['Minor gap'] : ['Critical element missing'],
        remediationTime: risk === 'CRITICAL' ? '1-3 days' : risk === 'HIGH' ? '3-7 days' : risk === 'MEDIUM' ? '7-14 days' : 'N/A'
      });
      chartNum++;
    }
  });
  
  return charts.sort((a, b) => {
    const riskOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
    return riskOrder[a.riskLevel] - riskOrder[b.riskLevel];
  });
};

const AuditShieldMobile = () => {
  const [charts] = useState(generateSampleCharts());
  const [selectedChart, setSelectedChart] = useState(null);
  const [view, setView] = useState('queue'); // 'queue', 'detail', 'progress'
  const [filter, setFilter] = useState('ALL');
  
  const riskColors = {
    CRITICAL: 'bg-red-100 border-red-500 text-red-900',
    HIGH: 'bg-orange-100 border-orange-500 text-orange-900',
    MEDIUM: 'bg-yellow-100 border-yellow-500 text-yellow-900',
    LOW: 'bg-green-100 border-green-500 text-green-900'
  };
  
  const riskBadgeColors = {
    CRITICAL: 'bg-red-500 text-white',
    HIGH: 'bg-orange-500 text-white',
    MEDIUM: 'bg-yellow-500 text-gray-900',
    LOW: 'bg-green-500 text-white'
  };
  
  const filteredCharts = filter === 'ALL' 
    ? charts 
    : charts.filter(c => c.riskLevel === filter);
  
  const stats = {
    total: charts.length,
    critical: charts.filter(c => c.riskLevel === 'CRITICAL').length,
    high: charts.filter(c => c.riskLevel === 'HIGH').length,
    medium: charts.filter(c => c.riskLevel === 'MEDIUM').length,
    low: charts.filter(c => c.riskLevel === 'LOW').length,
    compliant: charts.filter(c => c.riskLevel === 'LOW').length,
    complianceRate: ((charts.filter(c => c.riskLevel === 'LOW').length / charts.length) * 100).toFixed(1)
  };
  
  const AuditQueueView = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 to-blue-700 text-white p-4 sticky top-0 z-10 shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h1 className="text-xl font-bold">AuditShield Live</h1>
            <p className="text-blue-200 text-sm">CMS Audit Intelligence</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{stats.complianceRate}%</div>
            <div className="text-xs text-blue-200">Compliant</div>
          </div>
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-2 text-center text-xs">
          <div className="bg-red-500/20 rounded p-2 border border-red-400">
            <div className="font-bold text-lg">{stats.critical}</div>
            <div className="text-red-200">Critical</div>
          </div>
          <div className="bg-orange-500/20 rounded p-2 border border-orange-400">
            <div className="font-bold text-lg">{stats.high}</div>
            <div className="text-orange-200">High</div>
          </div>
          <div className="bg-yellow-500/20 rounded p-2 border border-yellow-400">
            <div className="font-bold text-lg">{stats.medium}</div>
            <div className="text-yellow-200">Medium</div>
          </div>
          <div className="bg-green-500/20 rounded p-2 border border-green-400">
            <div className="font-bold text-lg">{stats.low}</div>
            <div className="text-green-200">Low</div>
          </div>
        </div>
      </div>
      
      {/* Filter Buttons */}
      <div className="bg-white border-b border-gray-200 p-3 flex gap-2 overflow-x-auto">
        {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap ${
              filter === f 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            {f} {f !== 'ALL' && `(${stats[f.toLowerCase()]})`}
          </button>
        ))}
      </div>
      
      {/* Chart List */}
      <div className="p-3 space-y-2">
        {filteredCharts.slice(0, 50).map(chart => (
          <div
            key={chart.id}
            onClick={() => {
              setSelectedChart(chart);
              setView('detail');
            }}
            className={`p-3 rounded-lg border-l-4 shadow-sm cursor-pointer transition-all hover:shadow-md ${riskColors[chart.riskLevel]}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div>
                <div className="font-mono text-sm font-bold">{chart.id}</div>
                <div className="text-xs opacity-75">{chart.memberId}</div>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-bold ${riskBadgeColors[chart.riskLevel]}`}>
                {chart.riskLevel}
              </span>
            </div>
            
            <div className="text-sm font-medium mb-1">{chart.measureName}</div>
            
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1">
                  <TrendingUp size={12} />
                  {chart.complianceScore}/100
                </span>
                <span className="flex items-center gap-1">
                  <AlertCircle size={12} />
                  {(chart.failureProbability * 100).toFixed(0)}% fail
                </span>
              </div>
              <span className="font-mono">⭐ {chart.starImpact}</span>
            </div>
          </div>
        ))}
        
        {filteredCharts.length > 50 && (
          <div className="text-center text-sm text-gray-500 py-4">
            Showing first 50 of {filteredCharts.length} charts
          </div>
        )}
      </div>
      
      {/* Bottom Nav */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex">
        <button
          onClick={() => setView('queue')}
          className={`flex-1 py-3 text-center ${view === 'queue' ? 'text-blue-600 bg-blue-50' : 'text-gray-600'}`}
        >
          <FileText size={20} className="mx-auto mb-1" />
          <div className="text-xs font-medium">Queue</div>
        </button>
        <button
          onClick={() => setView('progress')}
          className={`flex-1 py-3 text-center ${view === 'progress' ? 'text-blue-600 bg-blue-50' : 'text-gray-600'}`}
        >
          <Clock size={20} className="mx-auto mb-1" />
          <div className="text-xs font-medium">Progress</div>
        </button>
      </div>
    </div>
  );
  
  const ChartDetailView = () => {
    if (!selectedChart) return null;
    
    return (
      <div className="min-h-screen bg-gray-50 pb-20">
        {/* Header */}
        <div className={`p-4 border-l-4 ${riskColors[selectedChart.riskLevel]}`}>
          <button
            onClick={() => setView('queue')}
            className="text-sm text-blue-600 mb-2"
          >
            ← Back to Queue
          </button>
          
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold font-mono">{selectedChart.id}</h2>
              <p className="text-sm opacity-75">Member: {selectedChart.memberId}</p>
            </div>
            <span className={`px-3 py-1 rounded-lg text-sm font-bold ${riskBadgeColors[selectedChart.riskLevel]}`}>
              {selectedChart.riskLevel}
            </span>
          </div>
          
          <div className="mt-3">
            <div className="text-lg font-medium">{selectedChart.measureName}</div>
            <div className="text-sm opacity-75">{selectedChart.measure}</div>
          </div>
        </div>
        
        {/* Metrics */}
        <div className="bg-white m-3 p-4 rounded-lg shadow-sm space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Compliance Score</span>
            <span className="text-lg font-bold">{selectedChart.complianceScore}/100</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Audit Failure Probability</span>
            <span className="text-lg font-bold text-red-600">{(selectedChart.failureProbability * 100).toFixed(0)}%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Star Rating Impact</span>
            <span className="text-lg font-bold">⭐ {selectedChart.starImpact} pts</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Est. Remediation Time</span>
            <span className="text-lg font-bold">{selectedChart.remediationTime}</span>
          </div>
        </div>
        
        {/* Multi-Source Intelligence */}
        {selectedChart.measure === 'CBP' && selectedChart.riskLevel !== 'LOW' && (
          <div className="m-3 space-y-3">
            {/* NCQA Requirements */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                <h3 className="font-bold text-sm">NCQA Requirements</h3>
              </div>
              <p className="text-sm text-gray-700">
                BOTH systolic AND diastolic BP required from SAME encounter. Most recent BP in measurement year is used.
              </p>
            </div>
            
            {/* CMS Audit Protocol */}
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-orange-600 rounded-full"></div>
                <h3 className="font-bold text-sm">CMS Audit Protocol</h3>
              </div>
              <p className="text-sm text-gray-700 mb-2">
                ⚠️ Missing one BP component is the #1 audit failure across all MA plans (30% of failures).
              </p>
              <p className="text-xs text-gray-600">
                Cross-encounter BP matching is explicitly prohibited.
              </p>
            </div>
            
            {/* Proprietary Intelligence */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                <h3 className="font-bold text-sm">Expert Playbook (22 years MA)</h3>
              </div>
              <div className="text-sm text-gray-700 space-y-2">
                <p className="font-medium">Remediation Strategy:</p>
                <ol className="list-decimal list-inside space-y-1 text-xs">
                  <li>Search encounter note for complete BP reading (XXX/XX format)</li>
                  <li>Contact clinic for vital signs from same visit</li>
                  <li>NEVER combine BP values from different encounters</li>
                  <li>DO NOT use patient-reported home BP readings</li>
                </ol>
                <p className="text-xs text-green-800 font-medium mt-2">
                  ROI Impact: 3.0 Star Rating weight + lowest pass rate = highest remediation priority
                </p>
              </div>
            </div>
          </div>
        )}
        
        {/* Action Button */}
        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-200">
          <button className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium shadow-lg">
            Assign for Remediation
          </button>
        </div>
      </div>
    );
  };
  
  const ProgressView = () => (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-blue-900 text-white p-4">
        <h2 className="text-xl font-bold mb-2">Audit Progress</h2>
        <p className="text-blue-200 text-sm">CMS Submission Timeline</p>
      </div>
      
      <div className="p-4 space-y-4">
        {/* Overall Progress */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex justify-between items-center mb-2">
            <span className="font-medium">Overall Compliance</span>
            <span className="text-2xl font-bold text-blue-600">{stats.complianceRate}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all"
              style={{ width: `${stats.complianceRate}%` }}
            ></div>
          </div>
          <div className="mt-2 text-sm text-gray-600">
            {stats.compliant} of {stats.total} charts audit-ready
          </div>
        </div>
        
        {/* Risk Breakdown */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <h3 className="font-medium mb-3">Charts by Risk Level</h3>
          
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-red-600 font-medium">CRITICAL</span>
                <span>{stats.critical} charts</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full"
                  style={{ width: `${(stats.critical / stats.total) * 100}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-orange-600 font-medium">HIGH</span>
                <span>{stats.high} charts</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-orange-500 h-2 rounded-full"
                  style={{ width: `${(stats.high / stats.total) * 100}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-yellow-600 font-medium">MEDIUM</span>
                <span>{stats.medium} charts</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-yellow-500 h-2 rounded-full"
                  style={{ width: `${(stats.medium / stats.total) * 100}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-green-600 font-medium">LOW</span>
                <span>{stats.low} charts</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${(stats.low / stats.total) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Timeline */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <h3 className="font-medium mb-3">Remediation Timeline</h3>
          
          <div className="space-y-3 text-sm">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                <AlertCircle size={16} className="text-red-600" />
              </div>
              <div className="flex-1">
                <div className="font-medium">Critical Charts</div>
                <div className="text-xs text-gray-600">Address within 24-48 hours</div>
                <div className="mt-1 text-xs text-red-600 font-medium">{stats.critical} charts requiring immediate action</div>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0">
                <Clock size={16} className="text-orange-600" />
              </div>
              <div className="flex-1">
                <div className="font-medium">High Priority</div>
                <div className="text-xs text-gray-600">Complete within 1 week</div>
                <div className="mt-1 text-xs text-orange-600 font-medium">{stats.high} charts</div>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <CheckCircle size={16} className="text-green-600" />
              </div>
              <div className="flex-1">
                <div className="font-medium">Audit-Ready</div>
                <div className="text-xs text-gray-600">No action required</div>
                <div className="mt-1 text-xs text-green-600 font-medium">{stats.low} charts compliant</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Performance Stats */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-500 rounded-lg p-4 text-white shadow-lg">
          <h3 className="font-medium mb-3">AuditShield Performance</h3>
          
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-blue-200 text-xs">Processing Time</div>
              <div className="text-2xl font-bold">0.55ms</div>
              <div className="text-xs text-blue-200">per chart</div>
            </div>
            
            <div>
              <div className="text-blue-200 text-xs">Accuracy</div>
              <div className="text-2xl font-bold">100%</div>
              <div className="text-xs text-blue-200">validated</div>
            </div>
            
            <div>
              <div className="text-blue-200 text-xs">Time Saved</div>
              <div className="text-2xl font-bold">322.5</div>
              <div className="text-xs text-blue-200">hours vs manual</div>
            </div>
            
            <div>
              <div className="text-blue-200 text-xs">Cost Savings</div>
              <div className="text-2xl font-bold">$1.59M</div>
              <div className="text-xs text-blue-200">ROI per cycle</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Bottom Nav */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex">
        <button
          onClick={() => setView('queue')}
          className={`flex-1 py-3 text-center ${view === 'queue' ? 'text-blue-600 bg-blue-50' : 'text-gray-600'}`}
        >
          <FileText size={20} className="mx-auto mb-1" />
          <div className="text-xs font-medium">Queue</div>
        </button>
        <button
          onClick={() => setView('progress')}
          className={`flex-1 py-3 text-center ${view === 'progress' ? 'text-blue-600 bg-blue-50' : 'text-gray-600'}`}
        >
          <Clock size={20} className="mx-auto mb-1" />
          <div className="text-xs font-medium">Progress</div>
        </button>
      </div>
    </div>
  );
  
  return (
    <div className="max-w-md mx-auto bg-white">
      {view === 'queue' && <AuditQueueView />}
      {view === 'detail' && <ChartDetailView />}
      {view === 'progress' && <ProgressView />}
    </div>
  );
};

export default AuditShieldMobile;
