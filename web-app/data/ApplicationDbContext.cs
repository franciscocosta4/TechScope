using Microsoft.EntityFrameworkCore;
using TechScope.Models;

namespace TechScope.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<Company> Companies => Set<Company>();
        public DbSet<Job> Jobs => Set<Job>();
        public DbSet<Technology> Technologies => Set<Technology>();
        public DbSet<JobTechnology> JobTechnologies => Set<JobTechnology>();

        protected override void OnModelCreating(ModelBuilder builder)
        {
            builder.Entity<Company>()
                .ToTable("Companies", table => table.ExcludeFromMigrations());
            builder.Entity<Company>()
                .HasKey(company => company.Id);

            builder.Entity<Job>()
                .ToTable("Jobs", table => table.ExcludeFromMigrations());
            builder.Entity<Job>()
                .HasKey(job => job.Id);
            builder.Entity<Job>()
                .HasOne(job => job.Company)
                .WithMany(company => company.Jobs)
                .HasForeignKey(job => job.CompanyId)
                .OnDelete(DeleteBehavior.Cascade);

            builder.Entity<Technology>()
                .ToTable("Technologies", table => table.ExcludeFromMigrations());
            builder.Entity<Technology>()
                .HasKey(technology => technology.Id);

            builder.Entity<JobTechnology>()
                .ToTable("JobTechnologies", table => table.ExcludeFromMigrations());
            builder.Entity<JobTechnology>()
                .HasKey(jobTechnology => new
                {
                    jobTechnology.JobId,
                    jobTechnology.TechnologyId
                });

            builder.Entity<JobTechnology>()
                .HasOne(jobTechnology => jobTechnology.Job)
                .WithMany(job => job.JobTechnologies)
                .HasForeignKey(jobTechnology => jobTechnology.JobId)
                .OnDelete(DeleteBehavior.Cascade);

            builder.Entity<JobTechnology>()
                .HasOne(jobTechnology => jobTechnology.Technology)
                .WithMany(technology => technology.JobTechnologies)
                .HasForeignKey(jobTechnology => jobTechnology.TechnologyId)
                .OnDelete(DeleteBehavior.Cascade);
        }
    }
}
