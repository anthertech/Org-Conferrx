export function formatDateRange(startDateStr, endDateStr) {
    const options = { month: 'short', day: 'numeric', year: 'numeric' };
    
    const startDate = new Date(startDateStr);
    const endDate = new Date(endDateStr);
  
    const startDay = startDate.getDate();
    const endDay = endDate.getDate();
  
    const startFormatter = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' });
    const endFormatter = new Intl.DateTimeFormat('en-US', { year: 'numeric' });
  
    if (startDate.getMonth() === endDate.getMonth() && startDate.getFullYear() === endDate.getFullYear()) {
      return `${startFormatter.format(startDate)} – ${endDay}, ${endFormatter.format(endDate)}`;
    } else {
      const fullStartFormatter = new Intl.DateTimeFormat('en-US', options);
      const fullEndFormatter = new Intl.DateTimeFormat('en-US', options);
      return `${fullStartFormatter.format(startDate)} – ${fullEndFormatter.format(endDate)}`;
    }
  }