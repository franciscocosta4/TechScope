using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using TechScope.Data;
using TechScope.Models;
using TechScope.ViewModels;

namespace TechScope.Controllers;

public class TechnologyController : Controller
{
    private readonly ApplicationDbContext _context;

    public TechnologyController(ApplicationDbContext context)
    {
        _context = context;
    }

    // GET: /technologies/{keyword}
    public async Task<IActionResult> Detail(string keyword)
    {
        if (string.IsNullOrWhiteSpace(keyword))
            return BadRequest();

        var keywordLower = keyword.ToLower();

        // Total de anúncios que mencionam esta tecnologia
        var totalJobs = await _context.JobKeywords
            .Where(jk => jk.Category == "technology" && jk.Keyword.ToLower() == keywordLower)
            .Select(jk => jk.JobId)
            .Distinct()
            .CountAsync();

        // Tendência mensal (últimos 12 meses)
        var twelveMonthsAgo = DateTime.UtcNow.AddMonths(-12);
        
        var monthlyTrendData = await _context.JobKeywords
            .Where(jk => jk.Category == "technology" 
                      && jk.Keyword.ToLower() == keywordLower
                      && jk.Job.DatePosted >= twelveMonthsAgo)
            .GroupBy(jk => new { jk.Job.DatePosted.Value.Year, jk.Job.DatePosted.Value.Month })
            .Select(g => new
            {
                Year = g.Key.Year,
                Month = g.Key.Month,
                JobCount = g.Select(jk => jk.JobId).Distinct().Count()
            })
            .OrderByDescending(m => m.Year)
            .ThenByDescending(m => m.Month)
            .ToListAsync();

        var monthlyTrend = monthlyTrendData
            .Select(m => new MonthlyTrend
            {
                Month = $"{m.Year}-{m.Month:D2}",
                JobCount = m.JobCount
            })
            .ToList();

        // Tecnologias relacionadas (co-ocorrência)
        var relatedTechnologies = await _context.JobKeywords
            .Where(jk => jk.Category == "technology" && jk.Keyword.ToLower() == keywordLower)
            .SelectMany(jk => _context.JobKeywords
                .Where(related => related.JobId == jk.JobId 
                               && related.Category == "technology" 
                               && related.Keyword.ToLower() != keywordLower)
                .Select(related => related.Keyword))
            .GroupBy(k => k)
            .Select(g => new TechnologyInfo
            {
                Keyword = g.Key,
                JobCount = g.Count()
            })
            .OrderByDescending(t => t.JobCount)
            .Take(10)
            .ToListAsync();

        // Empresas que recrutam
        var topCompanies = await _context.JobKeywords
            .Where(jk => jk.Category == "technology" && jk.Keyword.ToLower() == keywordLower)
            .GroupBy(jk => new { jk.Job.Company.Name, jk.Job.Company.Location })
            .Select(g => new CompanyInfo
            {
                Name = g.Key.Name,
                Location = g.Key.Location,
                JobCount = g.Select(jk => jk.JobId).Distinct().Count()
            })
            .OrderByDescending(c => c.JobCount)
            .Take(10)
            .ToListAsync();

        // Anúncios recentes relacionados
        var recentJobs = await _context.JobKeywords
            .Where(jk => jk.Category == "technology" && jk.Keyword.ToLower() == keywordLower)
            .Select(jk => new RecentJobInfo
            {
                Id = jk.JobId,
                Title = jk.Job.Title,
                CompanyName = jk.Job.Company.Name,
                Source = jk.Job.Source,
                ExternalId = jk.Job.ExternalId,
                DatePosted = jk.Job.DatePosted
            })
            .Distinct()
            .OrderByDescending(j => j.DatePosted)
            .Take(20)
            .ToListAsync();

        var model = new TechnologyDetailViewModel
        {
            Keyword = keyword,
            TotalJobs = totalJobs,
            MonthlyTrend = monthlyTrend,
            RelatedTechnologies = relatedTechnologies,
            TopCompanies = topCompanies,
            RecentJobs = recentJobs
        };

        return View(model);
    }
}
